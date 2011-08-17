from django.db import models
from django_durationRel.fields import DurationRelField


class OneByString(models.Model):
    """
    You can refer to another model by string reference which is discouraged
    but possible if that other model hasn't been loaded yet.
    """
    code = models.CharField(max_length=128)
    others = DurationRelField('Other')


class Other(models.Model):
    code = models.CharField(max_length=128)


class One(models.Model):
    code = models.CharField(max_length=128)
    others = DurationRelField(Other)
