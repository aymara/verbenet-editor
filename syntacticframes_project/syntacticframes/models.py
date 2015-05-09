from time import gmtime, strftime
import logging

from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from loadmapping.mappedverbs import translations_for_class
from parsecorrespondance.parse import FrenchMapping


# Levin class 9..104
class LevinClass(models.Model):
    STATUS_TRANSLATED = 'TRANSLATED'
    STATUS_REMOVED = 'REMOVED'
    STATUS_INPROGRESS = 'INPROGRESS'  # default status: not translated yet

    TRANSLATION_STATUS = (
        (STATUS_TRANSLATED, 'Translated'),
        (STATUS_REMOVED, 'Removed'),
        (STATUS_INPROGRESS, 'In progress'),
    )

    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    comment = models.TextField(max_length=100000, blank=True)
    translation_status = models.CharField(
        max_length=10, choices=TRANSLATION_STATUS,
        default=STATUS_INPROGRESS)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return "{}: {}".format(self.number, self.name)


# Class (9.3, 13.4.2, 107, etc.)
class VerbNetClass(models.Model):
    """A high-level VerbNet class (eg. put-9.1)"""
    levin_class = models.ForeignKey(LevinClass)
    name = models.CharField(max_length=100)
    comment = models.TextField(max_length=100000, blank=True)
    position = models.PositiveSmallIntegerField()

    def number(self):
        class_number = self.name.split('-')[1]
        if '.' in class_number:
            class_number = class_number.split('.')[0]

        return class_number

    class Meta:
        # Order at least by Levin class and alphabetical order
        ordering = ['position']

    def __str__(self):
        return self.name

    def update_members_and_translations(self):
        root_frameset = self.verbnetframeset_set.get(parent=None)
        root_frameset.update_members()
        root_frameset.update_manual_translations()
        root_frameset.update_translations()


# Subclass (9.1, 9.1-2, ...)
class VerbNetFrameSet(MPTTModel):
    """
    FrameSet which will contain sub-classes.

    A given subclass contains members, roles, and frames.
    """
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

    verbnet_class = models.ForeignKey(VerbNetClass)
    name = models.CharField(max_length=100)

    has_removed_frames = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)

    paragon = models.CharField(max_length=100, blank=True)
    comment = models.TextField(max_length=100000, blank=True)
    ladl_string = models.TextField(blank=True)
    lvf_string = models.TextField(blank=True)

    class MPTTMeta:
        # Using the name as a proxy for ordering in the tree is convenient, but
        # not guaranteed to always be 100% correct. As long as we have less
        # than 10 children, the name will work fine: '8' < '9'. If we have more
        # than 10 children, then we'll start to see issues: '10' < '2'.
        # Having more than 9 children already happen with VerbNet classes
        # (fire-10.10, resign-10.11), but is unlikely with subclasses.
        # Moreover, it's not that awful if the order is only 99% correct.
        order_insertion_by = ['name']

    def __str__(self):
        return 'VerbNetFrameSet: {}'.format(self.name)

    def lvf_parts(self):
        return FrenchMapping('LVF', self.lvf_string).flat_parse()

    def ladl_parts(self):
        return FrenchMapping('LADL', self.ladl_string).flat_parse()

    def check_has_removed_frames(self):
        self.has_removed_frames = self.verbnetframe_set.filter(removed=True)
        self.save()

    def mark_as_removed(self):
        assert not self.removed
        self.removed = True
        self.save()
        self.verbnet_class.update_members_and_translations()

    def mark_as_shown(self):
        assert self.removed
        self.removed = False
        self.save()
        self.verbnet_class.update_members_and_translations()

    # I can't get `get_ancestors` to work, so here's the slow way
    def get_parents(self, include_self=False):
        current_frameset = self

        if include_self:
            yield self

        while current_frameset.parent is not None:
            yield current_frameset.parent
            current_frameset = current_frameset.parent

    def move_members_and_verbs_to(self, other_frameset):
        # We don't want to have received_from = self, so prevent moving frames
        # to ourself. With normal users this shouldn't happen anyway as the UI
        # doesn't allow this.
        assert self.name != other_frameset.name

        # Move all members
        for member in self.get_all_verbs(VerbNetMember):
            member.inherited_from = None
            if member.received_from is None:
                member.received_from = self
            member.frameset = other_frameset
            member.save()

        # Move all validated or invalidated translations
        for translation in self.get_all_verbs(VerbTranslation):
            translation.inherited_from = None
            if translation.received_from is None:
                translation.received_from = self
            translation.frameset = other_frameset
            if translation.validation_status != VerbTranslation.STATUS_INFERRED:
                # We keep all invalidated translations, even if they no longer
                # have a color in the target frameset
                translation.save()

        # Ensure left-over inferred translations are removed
        self.verbnet_class.update_members_and_translations()
        # Ensure new translations are added
        other_frameset.verbnet_class.update_members_and_translations()

    def change_status(self, category, new_status):
        for verb_translation in self.verbtranslation_set.filter(category=category):
            verb_translation.validation_status = new_status
            verb_translation.save()

    def validate_verbs(self, category):
        self.change_status(category, VerbTranslation.STATUS_VALID)

    def update_translations(self):
        self.update_translations_aux(self.ladl_string, self.lvf_string)

    def update_translations_aux(self, ladl_string, lvf_string):
        """
        Updates translations given members in class and ladl_string/lvf_string
        parameters.

        ladl_string and lvf_string can be different from self.ladl_string and
        self.lvf_string if we're using an inherited lvf or ladl string, eg. if
        the current node's string is unset but his parent's string is set.

        If you're modifying this function, look at tools.views.errors_for_class
        too which also uses the ladl/lvf inheritance logic."""

        def in_parents(frameset, french, categoryname):
            for parent_frameset in frameset.get_parents():
                for translation in parent_frameset.verbtranslation_set.all():
                    if translation.verb == french:
                        #assert categoryname in ['unknown', 'dicovalence'] and translation.category in ['ladl', 'lvf', 'both']
                        return True

            return False

        translations_in_subclasses = []

        for db_childrenfs in self.children.filter(removed=False):
            new_ladl = ladl_string if not db_childrenfs.ladl_string else db_childrenfs.ladl_string
            new_lvf = lvf_string if not db_childrenfs.lvf_string else db_childrenfs.lvf_string
            translations_in_subclasses.extend(db_childrenfs.update_translations_aux(ladl_string=new_ladl, lvf_string=new_lvf))

        initial_set = {(v.verb, v.category, v.validation_status) for v in self.verbtranslation_set.all()}
        moved_set = set()
        inferred_verbs = self.verbtranslation_set.filter(validation_status=VerbTranslation.STATUS_INFERRED)
        inferred_verbs.delete()
        manually_validated_verbs = self.verbtranslation_set.exclude(validation_status=VerbTranslation.STATUS_INFERRED)
        manually_validated_set = {v.verb: v.category for v in manually_validated_verbs}
        when_deleted = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        members = [m.lemma for m in self.verbnetmember_set.all()]
        candidates = translations_for_class(members, ladl_string, lvf_string)

        verb_logger = logging.getLogger('verbs')

        for french, categoryname, category_id, originlist in candidates:
            originset = set(originlist.split(','))
            if set(members) & originset:  # is actually a translation

                # At this point we have four options.
                #  1/ this translation was added below but hidden: we can show
                #  it here unhidden, which is better.
                same_verb_below_list = [v for v in translations_in_subclasses if v.verb == french]

                if same_verb_below_list:
                    for same_verb_below in same_verb_below_list:
                        # Don't touch validated verbs
                        if same_verb_below.validation_status != VerbTranslation.STATUS_INFERRED:
                            continue

                        if categoryname in ['ladl', 'lvf', 'both'] and same_verb_below.category in ['dicovalence', 'unknown']:
                            previous_subclass = same_verb_below.frameset
                            previous_category = same_verb_below.category
                            same_verb_below.frameset = self
                            same_verb_below.category = categoryname
                            same_verb_below.category_id = VerbTranslation.CATEGORY_ID[categoryname]
                            same_verb_below.save()
                            moved_set.add((same_verb_below.verb, same_verb_below.category, same_verb_below.validation_status))
                            translations_in_subclasses = [v for v in translations_in_subclasses if v.verb != french]
                            verb_logger.info("{}: Moved {} up from subclass {} to subclass {} ({} -> {}).".format(
                                when_deleted, french, previous_subclass.name, self.name, previous_category, categoryname))

                #  2/ this translation was not manually validated at all: add it
                elif french not in manually_validated_set:
                    # Make sure not to add a verb that was already moved up to
                    # parents in a previous run
                    if not (in_parents(self, french, categoryname) and categoryname in ['unknown', 'dicovalence']):
                        VerbTranslation(
                            frameset=self, verb=french, origin=originlist,
                            category=categoryname,
                            category_id=VerbTranslation.CATEGORY_ID[categoryname]).save()
                #  3/ this translation was manually validated but with a different
                #  status: change the status
                elif categoryname != manually_validated_set[french]:
                    verb_to_update = VerbTranslation.objects.get(
                        frameset=self, verb=french, category=manually_validated_set[french])
                    verb_to_update.category = categoryname
                    verb_to_update.category_id = VerbTranslation.CATEGORY_ID[categoryname]
                    verb_to_update.save()
                #  4/ this translation was manually validated and already has
                #  the correct color: do nothing
                else:
                    pass

        when_added = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        verbs = self.verbtranslation_set.all()
        final_set = {(v.verb, v.category, v.validation_status) for v in verbs}

        if initial_set - final_set:
            verb_logger.info("{}: Removed verbs in subclass {}: {}".format(
                when_deleted, self.name, ", ".join(["{} ({}, {})".format(v, c, s) for v, c, s in sorted(initial_set - final_set, key=lambda vcs: vcs[0])])))
        if (final_set - initial_set) - moved_set:  # parens for clarity only
            verb_logger.info("{}: Added verbs in subclass {}: {}".format(
                when_deleted, self.name, ", ".join(["{} ({}, {})".format(v, c, s) for v, c, s in sorted(final_set - initial_set, key=lambda vcs: vcs[0])])))

        return list(verbs) + translations_in_subclasses

    def get_all_verbs(self, VerbModule):
        """Recursively retrieve members from all subclasses"""
        related_name = '{}_set'.format(VerbModule._meta.model_name)

        objects = set(getattr(self, related_name).all())

        for child_fs in self.children.all():
            objects |= child_fs.get_all_verbs(VerbModule)

        return objects

    def update_members(self):
        """Moves members according to hidden/shown classes

        If a subclass was hidden, all members should show up in the first
        superclass that is not hidden. If a subclass was shown, any member that
        was moved up should go down again."""
        verb_logger = logging.getLogger('verbs')

        members_to_move = []
        for member in self.get_all_verbs(VerbNetMember):
            inherited_from = member.inherited_from if member.inherited_from else member.frameset

            best_frameset = None
            for parent in inherited_from.get_parents(include_self=True):
                if not parent.removed:
                    best_frameset = parent
                    break

            if best_frameset is not None and member.frameset != best_frameset:
                members_to_move.append({
                    'member': member,
                    'inherited_from': inherited_from,
                    'wanted_frameset': best_frameset})

        for add_member in members_to_move:
            member = add_member['member']
            previous_frameset = member.frameset
            member.frameset = add_member['wanted_frameset']
            if member.frameset == add_member['inherited_from']:
                member.inherited_from = None
            else:
                member.inherited_from = add_member['inherited_from']
            member.save()
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            verb_logger.info("{}: Moved member {} from {} to {}".format(
                when, member.lemma, previous_frameset, member.frameset))

    def update_manual_translations(self):
        """Moves manual translations according to hidden/shown classes

        We treat manual translations exactly as members in self.update_members
        here: they were manually validated or added and should not simply be
        deleted and inferred again as automatic translation can be. (A "manual"
        translation is a translation that was validated manually by clicking on
        a verb in the interface OR that was added by clicking on the "plus"
        link).
        """
        verb_logger = logging.getLogger('verbs')

        translations_to_move = []
        for translation in self.get_all_verbs(VerbTranslation):
            if translation.validation_status == VerbTranslation.STATUS_INFERRED:
                continue

            inherited_from = translation.inherited_from if translation.inherited_from else translation.frameset

            best_frameset = None
            for parent in inherited_from.get_parents(include_self=True):
                if not parent.removed:
                    best_frameset = parent
                    break

            if best_frameset is not None and translation.frameset != best_frameset:
                translations_to_move.append({
                    'translation': translation,
                    'inherited_from': inherited_from,
                    'wanted_frameset': best_frameset})

        for add_translation in translations_to_move:
            translation = add_translation['translation']
            previous_frameset = translation.frameset
            translation.frameset = add_translation['wanted_frameset']
            translation.inherited_from = add_translation['inherited_from']
            translation.save()
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            verb_logger.info("{}: Moved translation {} from {} to {}".format(
                when, translation.verb, previous_frameset, translation.frameset))

    def update_roles(self):
        role_list = self.verbnetrole_set.all()
        i = 0

        for role in role_list:
            role.position = i
            role.save()
            i += 1

        return i


# English member
class VerbNetMember(models.Model):
    """An english member"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    # Members that were inherited from another *hidden* frameset
    inherited_from = models.ForeignKey(VerbNetFrameSet, null=True, blank=True,
                                       related_name='inheritedmember_set')
    # Members that were sent from another frameset
    received_from = models.ForeignKey(VerbNetFrameSet, null=True, blank=True,
                                      related_name='receivedmember_set')
    lemma = models.CharField(max_length=1000)

    def __str__(self):
        return self.lemma

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.frameset == other.frameset and self.inherited_from == other.inherited_from and self.lemma == other.lemma

    def __repr__(self):
        inherited_from_name = self.inherited_from.name if self.inherited_from else "None"
        received_from_name = self.received_from.name if self.received_from else "None"
        return "VerbNetMember({} ({}) i{}, r{})".format(self.lemma, self.frameset.name,
                                                         inherited_from_name, received_from_name)

    def __hash__(self):
        return hash(self.__repr__())

    class Meta:
        ordering = ['lemma']

        # We want to prevent accidental members duplications here and are using
        # SQL UNIQUE to do so. To explain why the unique constraints are laid
        # this way, let's talk about an hypothetical scenario that this doesn't
        # cover.

        # 1/ Say you have a class A with children A.1 and A.2 and say both
        # children have the same member (same WordNet and OntoNotes sense).
        # This does happen in VerbNet 3.2, see incorporate in
        # amalgamate-22.2-2.
        # 2/ Say you hide both A.1 and A.2 because they don't fit in your
        # target language: you now receive two *different* `incorporate` since
        # they come from different classes. You should of course keep the two
        # versions, should you decide to unhide the classes one day. However,
        # you should only show one of them at display time, eg. by using a
        # Python set to send the verb classes to the template. So far so good.
        # 3/ You send the verbs of class A to class B, including `incorporate`.
        # At this point, you have two `incorporate` with the same received_from
        # field (A) but different inherited_from field (A.1 and A.2). They're
        # different, and we want to allow that in PostgreSQL.

        # To accept this scenario, we first define unique_together as ('lemma',
        # 'inherited_from', 'received_from'). However, with only this, many
        # incorrect situations will be incorrectly accepted. Indeed, null
        # values are not considered equal
        # (http://www.postgresql.org/docs/9.4/static/indexes-unique.html). This
        # is why we're also setting two other constraints, each one handling
        # the possibility that the left-out column be null.

        unique_together = (
            ('lemma', 'inherited_from', 'received_from'),
            ('lemma', 'inherited_from'), ('lemma', 'received_from'))


# Frame: NP V, Agent V, Pred(Agent, E)
class VerbNetFrame(models.Model):
    frameset = models.ForeignKey(VerbNetFrameSet)

    # Metadata
    position = models.PositiveSmallIntegerField(null=True)
    removed = models.BooleanField(default=False)
    from_verbnet = models.BooleanField(default=True)

    # NP V NP
    syntax = models.CharField(max_length=1000)
    # John confesses it
    example = models.CharField(max_length=1000)
    # Agent V Topic
    roles_syntax = models.CharField(max_length=1000)
    # transfer_info(during(E), Agent, ?Recipient, Topic) cause(Agent, E)
    semantics = models.CharField(max_length=1000)

    def __str__(self):
        return "{} ({})".format(self.syntax, self.example)

    def save(self, *args, **kwargs):
        super(VerbNetFrame, self).save(*args, **kwargs)
        self.frameset.check_has_removed_frames()

    class Meta:
        ordering = ['position']


# Role (Agent[+animate])
class VerbNetRole(models.Model):
    """One role for a specific VerbNetFrameSet"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    # name + restrictions
    name = models.CharField(max_length=1000)
    position = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']


# Translation
class VerbTranslation(models.Model):
    TRANSLATION_CATEGORY = (
        ('both', 'Both'),
        ('ladl', 'LADL'),
        ('lvf', 'LVF'),
        ('dicovalence', 'Dicovalence'),
        ('unknown', 'No category'),
    )

    CATEGORY_ID = {
        'both': 0,
        'ladl': 1,
        'lvf': 2,
        'dicovalence': 3,
        'unknown': 4,
    }

    STATUS_INFERRED = 'INFERRED'
    STATUS_VALID = 'VALID'
    STATUS_WRONG = 'WRONG'
    VALIDATION_STATUS = (
        (STATUS_INFERRED, 'Inferred'),
        (STATUS_VALID, 'Valid'),
        (STATUS_WRONG, 'Wrong'),
    )

    frameset = models.ForeignKey(VerbNetFrameSet)
    verb = models.CharField(max_length=100)

    category = models.CharField(max_length=20, choices=TRANSLATION_CATEGORY)
    # id, used for ordering
    category_id = models.PositiveSmallIntegerField()
    # english comma-separated verbs
    origin = models.CharField(max_length=500, blank=True)
    # has this verb been manually validated?
    validation_status = models.CharField(
        max_length=10, choices=VALIDATION_STATUS,
        default=STATUS_INFERRED)
    # when hiding classes, manual translations and members can move: we want to
    # keep track of their initial position
    inherited_from = models.ForeignKey(VerbNetFrameSet, null=True, blank=True,
                                       related_name='inheritedmanualtranslation_set')
    # It's also possible for a frameset to send manually validated verbs
    # (including translations) to another one: we keep track of it here.
    received_from = models.ForeignKey(VerbNetFrameSet, null=True, blank=True,
                                      related_name='receivedtranslation_set')

    def __str__(self):
        return "{} ({}, {})".format(self.verb, self.category, self.validation_status)

    class Meta:
        ordering = ['category_id', 'verb']

    def togglevalidity(self, new_status):
        assert new_status in ['WRONG', 'VALID', 'INFERRED']
        self.validation_status = new_status
        self.save()

    @staticmethod
    def all_valid(translation_qs):
        """Returns the list of all valid VerbTranslation

        At some point, the "valid" translation will only be manually validated
        verbs. However, when no valid translation exist, we want to use the
        purple, red or green list."""

        translation_list = list(translation_qs)
        manually_validated = {
            v for v in translation_list
            if v.validation_status == VerbTranslation.STATUS_VALID}
        purple_verbs = {
            v for v in translation_list
            if v.category == 'both'
            and v.validation_status == VerbTranslation.STATUS_INFERRED}

        if manually_validated:
            inferred = set()
        elif purple_verbs:
            inferred = purple_verbs
        else:
            inferred = {
                v for v in translation_list
                if v.category in ['ladl', 'lvf']
                and v.validation_status == VerbTranslation.STATUS_INFERRED}

        return manually_validated | inferred
