from functools import total_ordering

from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


# Levin class 9..104
class LevinClass(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)


# Class (9.3, 13.4.2, 107, etc.)
class VerbNetClass(models.Model):
    """A high-level VerbNet class (eg. put-9.1)"""
    levin_class = models.ForeignKey(LevinClass)
    name = models.CharField(max_length=100)

    def number(self):
        class_number = self.name.split('-')[1]
        if '.' in class_number:
            class_number = class_number.split('.')[0]

        return class_number

    def __str__(self):
        return self.name


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
    comment = models.CharField(max_length=1000, blank=True)
    ladl_string = models.CharField(max_length=100, blank=True)
    lvf_string = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return 'VerbNetFrameSet: {}'.format(self.name)

    def check_has_removed_frames(self):
        self.has_removed_frames = self.verbnetframe_set.filter(removed=True)
        self.save()

    class Meta:
        ordering = ['id']


# English member
class VerbNetMember(models.Model):
    """An english member"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    lemma = models.CharField(max_length=1000)

    def __str__(self):
        return self.lemma

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
@total_ordering
class VerbTranslation(models.Model):
    TRANSLATION_CATEGORY = (
        ('both', 'Both'),
        ('ladl', 'LADL'),
        ('lvf', 'LVF'),
        ('dicovalence', 'Dicovalence'),
        ('unknown', 'No category'),
    )

    frameset = models.ForeignKey(VerbNetFrameSet)
    verb = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TRANSLATION_CATEGORY)
    # english comma-separated verbs
    origin = models.CharField(max_length=500)

    def __str__(self):
        return "{} ({})".format(self.verb, self.category)

    def __gt__(self, other):
        order = [x[0] for x in VerbTranslation.TRANSLATION_CATEGORY]
        if self.category == other.category:
            return self.verb > other.verb
        else:
            return order.index(self.category) > order.index(other.category)
