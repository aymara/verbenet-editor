from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from functools import total_ordering

class LevinClass(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

class VerbNetClass(models.Model):
    """A high-level VerbNet class (eg. put-9.1)"""
    levin_class = models.ForeignKey(LevinClass)
    name = models.CharField(max_length=100)
    paragon = models.CharField(max_length=100)
    comment = models.CharField(max_length=1000)
    ladl_string = models.CharField(max_length=100)
    lvf_string = models.CharField(max_length=100)

class VerbNetFrameSet(MPTTModel):
    """
    FrameSet which will contain sub-classes.

    A given subclass contains members, roles, and frames.
    """
    verbnet_class = models.ForeignKey(VerbNetClass)
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

class VerbNetMember(models.Model):
    """An english member"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    lemma = models.CharField(max_length=1000)

    def __str__(self):
        return self.lemma

class VerbNetRole(models.Model):
    """One role for a specific VerbNetFrameSet"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    # name + restrictions
    name = models.CharField(max_length=1000)

class VerbNetFrame(models.Model):
    frameset = models.ForeignKey(VerbNetFrameSet)
    position = models.PositiveSmallIntegerField(null=True)
    removed = models.BooleanField(default=False)
    # NP V NP
    syntax = models.CharField(max_length=1000) 
    # John confesses it
    example = models.CharField(max_length=1000) 
    # Agent V Topic
    roles_syntax = models.CharField(max_length=1000) 
    # transfer_info(during(E), Agent, ?Recipient, Topic) cause(Agent, E)
    semantics = models.CharField(max_length=1000)

    class Meta:
        ordering = ['position']

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
    origin = models.CharField(max_length=500) # english comma-separated verbs

    def __str__(self):
        return "{} ({})".format(self.verb, self.category)

    def __gt__(self, other):
        order = [x[0] for x in VerbTranslation.TRANSLATION_CATEGORY]
        return order.index(self.category) < order.index(other.category) and self.verb < other.verb
