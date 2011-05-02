from django.db import models
from django_durationRel.fields import DurationRelField

class Other(models.Model):
    code = models.CharField(max_length=128)

class One(models.Model):
    code = models.CharField(max_length=128)
    others = DurationRelField(Other)
