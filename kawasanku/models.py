from email.policy import default
import jsonfield
from django.db import models
from django.utils.translation import gettext_lazy as _

class Test(models.Model) :
    name = models.CharField(max_length=200)
    json = models.JSONField(max_length=200)

class JsonStore(models.Model) :
    general = models.JSONField()

class SnapshotJSON(models.Model) :
    general = models.JSONField()

class Doughnuts(models.Model) :
    general = models.JSONField()

class Pyramid(models.Model) : 
    general = models.JSONField()

class Links(models.Model) :
    general = models.JSONField()

class Geo(models.Model) :
    country = models.JSONField()
    state = models.JSONField()
    district = models.JSONField()
    parlimen = models.JSONField()
    dun = models.JSONField()

class Dropdown(models.Model) :
    dropdown = models.JSONField()

class Jitter(models.Model) :
    jitter = models.JSONField()

class AreaType(models.Model) :
    area = models.JSONField()