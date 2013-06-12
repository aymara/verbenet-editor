from django.db import models
from functools import total_ordering

class LevinClass(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

class VerbNetClass(models.Model):
    levin_class = models.ForeignKey(LevinClass)
    name = models.CharField(max_length=100)
    paragon = models.CharField(max_length=100)
    comment = models.CharField(max_length=1000)
    ladl_string = models.CharField(max_length=100)
    lvf_string = models.CharField(max_length=100)

class VerbNetMember(models.Model):
    verbnet_class = models.ForeignKey(VerbNetClass)
    lemma = models.CharField(max_length=1000)

@total_ordering
class VerbTranslation(models.Model):
    TRANSLATION_CATEGORY = (
        ('both', 'Both'),
        ('ladl', 'LADL'),
        ('lvf', 'LVF'),
        ('dicovalence', 'Dicovalence'),
        ('unknown', 'No category'),
    )

    verbnet_class = models.ForeignKey(VerbNetClass)
    verb = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TRANSLATION_CATEGORY)
    origin = models.CharField(max_length=500) # english comma-separated verbs

    def __str__(self):
        return "{} ({})".format(self.verb, self.category)

    def __lt__(self, other):
        order = [x[0] for x in VerbTranslation.TRANSLATION_CATEGORY]
        return order.index(self.category) < order.index(other.category)
    
    
    
