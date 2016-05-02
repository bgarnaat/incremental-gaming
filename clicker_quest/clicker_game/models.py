from __future__ import unicode_literals

from django.db import models
from django.conf import settings

# Create your models here.


class Clicker_Game(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='game')
    game_data = models.CharField()
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
