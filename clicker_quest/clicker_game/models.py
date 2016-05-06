from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from clicker_game.game_model import validate_game_model

# Create your models here.


class ClickerGame(models.Model):
    """Model for a general clicker game."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='games_owned')
    game_data = JSONField(validators=[validate_game_model])
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)


class GameInstance(models.Model):
    """Model for a single clicker game instance/state"""
    class meta:
        unique_together = ('user', 'game')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='games_playing')
    game = models.ForeignKey(ClickerGame, related_name='running_games')
    data = JSONField()
    modified = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)