from django.db import models

class LVFVerb(models.Model):
    lemma = models.CharField(max_length=100)
    sense = models.PositiveSmallIntegerField()

    lvf_class = models.CharField(max_length=10)
    # No encoding is contained into another, so using a simple TextField for
    # constructions instead of an enum is fine. We can search for 'T14b0', it
    # will work even if the constructions also contains 'T1300'.
    construction = models.TextField()

    def __str__(self):
        return self.lemma
