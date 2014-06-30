from django.db import models

class LVFVerb(models.Model):
    lemma = models.CharField(max_length=100)
    sense = models.PositiveSmallIntegerField()

    lvf_class = models.CharField(max_length=10)
    # No encoding is contained into another
    construction = models.TextField()

    def __str__(self):
        return self.lemma
