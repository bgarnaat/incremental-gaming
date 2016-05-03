from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from clicker_game.models import Game_Instance, Clicker_Game
from clicker_game.game_model import GameModel

# Create your views here.

# The starting resources/buildings/etc for a new game.


class MainView(View):
    """The View Used when loading a game.

    if a user is logged in it returns their game instance.
    Otherwise give a new game instance.
    """
    template_name = 'base.html'

    def get(self, request):
        game_model_data = Clicker_Game.objects.all()[0].game_data  # Get The Game Rules the User Is Playing
        model = GameModel(game_model_data)
        instance = model.load_game_instance()

        if request.user.is_authenticated():
            cur_vals = Game_Instance.objects.get(user=request.user).data
            return render(request, self.template_name, {'game': instance, 'vals': cur_vals})
        else:
            start_vals = game_model_data['new_game']
            return render(request, self.template_name, {'game': instance, 'vals': start_vals})


def purchase_building(request, building_name, num_purchased):
    game_model_data = Clicker_Game.objects.all()[0].game_data  # Get The Game Rules the User Is Playing
    instance = GameModel(game_model_data).load_game_instance()
    new_data = instance.purchase_building(request.GET['Date'], building_name, num_purchased)
    game_instance = Game_Instance.objects.get(user=request.user)
    game_instance.data = new_data
    game_instance.save()
    return render(request, 'base.html', {'game': instance, 'vals': game_instance.data})


def purchase_upgrade(request, upgrade_name):
    game_model_data = Clicker_Game.objects.all()[0].game_data  # Get The Game Rules the User Is Playing
    instance = GameModel(game_model_data).load_game_instance()
    new_data = instance.purchase_upgrade(request.GET['Date'], upgrade_name)
    game_instance = Game_Instance.objects.get(user=request.user)
    game_instance.data = new_data
    game_instance.save()
    return render(request, 'base.html', {'game': instance, 'vals': game_instance.data})
