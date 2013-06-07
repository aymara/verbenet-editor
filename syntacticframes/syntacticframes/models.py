from django.db import models

class LevinClass(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

class VerbNetClass(models.Model):
    levinclass = models.ForeignKey(LevinClass)
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    
    
