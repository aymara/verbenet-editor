from functools import total_ordering
from time import gmtime, strftime
import logging

from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from loadmapping.mappedverbs import translations_for_class
from parsecorrespondance.parse import FrenchMapping

# Levin class 9..104
class LevinClass(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    is_translated = models.BooleanField(default=False)
    comment = models.TextField(max_length=100000, blank=True)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)


# Class (9.3, 13.4.2, 107, etc.)
class VerbNetClass(models.Model):
    """A high-level VerbNet class (eg. put-9.1)"""
    levin_class = models.ForeignKey(LevinClass)
    name = models.CharField(max_length=100)
    comment = models.TextField(max_length=100000, blank=True)

    def number(self):
        class_number = self.name.split('-')[1]
        if '.' in class_number:
            class_number = class_number.split('.')[0]

        return class_number

    def __str__(self):
        return self.name

    def update_members_and_translations(self):
        root_frameset = self.verbnetframeset_set.get(parent=None)
        root_frameset.update_members(root_frameset)
        root_frameset.update_translations()


# Subclass (9.1-2)
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

    class Meta:
        ordering = ['id']

    def __str__(self):
        return 'VerbNetFrameSet: {}'.format(self.name)

    def lvf_parts(self):
        return FrenchMapping('LVF', self.lvf_string).flat_parse()

    def ladl_parts(self):
        return FrenchMapping('LADL', self.ladl_string).flat_parse()

    def check_has_removed_frames(self):
        self.has_removed_frames = self.verbnetframe_set.filter(removed=True)
        self.save()

    def update_translations(self, ladl_string=None, lvf_string=None):
        """
        Updates translations given members in class and ladl_string/lvf_string parameters.

        ladl_string and lvf_string can be different from self.ladl_string and
        self.lvf_string if we're using an inherited lvf or ladl string, eg. if the
        current node's string is unset but his parent's string is set.
        """

        if ladl_string is None:
            ladl_string = self.ladl_string

        if lvf_string is None:
            lvf_string = self.lvf_string

        translations_in_subclasses = set()

        for db_childrenfs in self.children.filter(removed=False):
            new_ladl = ladl_string if not db_childrenfs.ladl_string else db_childrenfs.ladl_string
            new_lvf = lvf_string if not db_childrenfs.lvf_string else db_childrenfs.lvf_string
            translations_in_subclasses |= db_childrenfs.update_translations(ladl_string=new_ladl, lvf_string=new_lvf)

        verbs = self.verbtranslation_set.all()
        initial_set = {(v.verb, v.category) for v in verbs}
        verbs.delete()
        first_when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        members = [m.lemma for m in self.verbnetmember_set.all()]
        candidates = translations_for_class(members, ladl_string, lvf_string)

        for french, categoryname, categoryid, originlist in candidates:
            originset = set(originlist.split(','))
            if set(members) & originset and french not in translations_in_subclasses:
                VerbTranslation(
                    frameset=self,
                    verb=french,
                    category=categoryname,
                    category_id=VerbTranslation.CATEGORY_ID[categoryname],
                    origin=originlist).save()

        last_when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        verbs = self.verbtranslation_set.all()
        final_set = {(v.verb, v.category) for v in verbs}
        translations_in_subclasses |= {v[0] for v in final_set}

        verb_logger = logging.getLogger('verbs')
        if initial_set - final_set:
            verb_logger.info("{}: Removed verbs in subclass {}: {}".format(
                first_when, self.name, ", ".join(["{} ({})".format(v, c) for v, c in initial_set - final_set])))
        if final_set - initial_set:
            verb_logger.info("{}: Added verbs in subclass {}: {}".format(
                last_when, self.name, ", ".join(["{} ({})".format(v, c) for v, c in final_set - initial_set])))

        return translations_in_subclasses


    def update_members(self, frameset):
        def get_all_members(frameset, parent_fs):
            """Recursively retrieve members from all subclasses"""
            members = frameset.verbnetmember_set.all()

            # We need to set this before putting members into a set
            for f in members:
                f.inherited_from = frameset
                f.frameset = parent_fs

            members = set(members)

            for child_fs in frameset.children.all():
                members |= get_all_members(child_fs, parent_fs)

            return members


        existing_inherited_members = set(frameset.verbnetmember_set.filter(inherited_from__isnull=False))

        real_inherited_members = set()

        for child_fs in frameset.children.all():
            if child_fs.removed:
                real_inherited_members |= get_all_members(child_fs, frameset)
            else:
                self.update_members(child_fs)

        verb_logger = logging.getLogger('verbs')
        if existing_inherited_members != real_inherited_members:
            for extra_inherited_member in existing_inherited_members - real_inherited_members:
                extra_inherited_member.delete()
                when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                verb_logger.info("{}: Removed {} (was inherited from {} in subclass {})".format(
                    when, extra_inherited_member.lemma, extra_inherited_member.inherited_from, extra_inherited_member.frameset))

            for missing_inherited_member in real_inherited_members - existing_inherited_members:
                missing_inherited_member.pk = None
                missing_inherited_member.save()
                when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                verb_logger.info("{}: Added {} (is inherited from {} in subclass {})".format(
                    when, missing_inherited_member.lemma, missing_inherited_member.inherited_from, missing_inherited_member.frameset))


# English member
class VerbNetMember(models.Model):
    """An english member"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    inherited_from = models.ForeignKey(VerbNetFrameSet, null=True, related_name='inheritedmember_set')
    lemma = models.CharField(max_length=1000)

    def __str__(self):
        return self.lemma

    def __eq__(self, other):
        return self.frameset == other.frameset and self.inherited_from == other.inherited_from and self.lemma == other.lemma

    def __repr__(self):
        return "VerbNetMember: {} ({}/{})".format(self.lemma, self.frameset.name,
            self.inherited_from.name if self.inherited_from else "None")

    def __hash__(self):
        return hash(self.__repr__())

    class Meta:
        ordering = ['lemma']


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

    frameset = models.ForeignKey(VerbNetFrameSet)
    verb = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TRANSLATION_CATEGORY)
    category_id = models.PositiveSmallIntegerField()
    # english comma-separated verbs
    origin = models.CharField(max_length=500)

    def __str__(self):
        return "{} ({})".format(self.verb, self.category)

    class Meta:
        ordering = ['category_id', 'verb']
