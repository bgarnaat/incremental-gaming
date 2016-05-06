from django.contrib import admin
from clicker_game.models import ClickerGame, GameInstance

# Register your models here.
admin.site.register(ClickerGame)
admin.site.register(GameInstance)
