from django.db import models
from django.contrib.auth.models import User
from legacy.models import Users

class Marker(models.Model):
    author = models.CharField(max_length = 30)
    title = models.CharField(max_length = 100)
    bodytext = models.TextField()
    timestamp = models.DateTimeField()


