from functools import total_ordering

from django.db import models
from django.contrib import admin

from mptt.models import MPTTModel, TreeForeignKey
import reversion

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
    paragon = models.CharField(max_length=100)
    comment = models.CharField(max_length=1000)
    ladl_string = models.CharField(max_length=100)
    lvf_string = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class VerbNetClassAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetClass, VerbNetClassAdmin)

# Subclass (9.1-2) 
class VerbNetFrameSet(MPTTModel):
    """
    FrameSet which will contain sub-classes.

    A given subclass contains members, roles, and frames.
    """
    verbnet_class = models.ForeignKey(VerbNetClass)
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class VerbNetFrameSetAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetFrameSet, VerbNetFrameSetAdmin)

# English member
class VerbNetMember(models.Model):
    """An english member"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    lemma = models.CharField(max_length=1000)

    def __str__(self):
        return self.lemma

class VerbNetMemberAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetMember, VerbNetMemberAdmin)

# Frame: NP V, Agent V, Pred(Agent, E)
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

    def __str__(self):
        return "{} ({})".format(self.syntax, self.example)

    class Meta:
        ordering = ['position']

class VerbNetFrameAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetFrame, VerbNetFrameAdmin)

# Role (Agent[+animate])
class VerbNetRole(models.Model):
    """One role for a specific VerbNetFrameSet"""
    frameset = models.ForeignKey(VerbNetFrameSet)
    # name + restrictions
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class VerbNetRoleAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetRole, VerbNetRoleAdmin)

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
    origin = models.CharField(max_length=500) # english comma-separated verbs

    def __str__(self):
        return "{} ({})".format(self.verb, self.category)

    def __gt__(self, other):
        order = [x[0] for x in VerbTranslation.TRANSLATION_CATEGORY]
        if self.category == other.category:
            return self.verb > other.verb
        else:
            return order.index(self.category) > order.index(other.category)

class VerbTranslationAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbTranslation, VerbTranslationAdmin)
