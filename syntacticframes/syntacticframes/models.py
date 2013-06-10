from django.db import models

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

class VerbTranslation(models.Model):
    TRANSLATION_CATEGORY = (
        ('both', 'Both'),
        ('ladl', 'LADL'),
        ('lvf', 'LVF'),
        ('dicovalence', 'Dicovalence'),
        ('none', 'No category'),
    )

    verbnet_class = models.ForeignKey(VerbNetClass)
    verb = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=TRANSLATION_CATEGORY)
    origin = models.CharField(max_length=500) # english comma-separated verbs
    
    
    
