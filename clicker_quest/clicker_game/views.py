from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from clicker_game.models import Game_Instance, Clicker_Game
from clicker_game.game_model import GameModel

# Create your views here.

# The starting resources/buildings/etc for a new game.


class MainView(View):
    """The View Used for a clicker game.

    if a user is logged in it returns their game instance.
    Otherwise give a new game instance.
    All post requests are done by ajax requests.
    """
    template_name = 'base.html'

    def get(self, request):
        game_model_data = Clicker_Game.objects.all()[0].game_data  # Get The Game Rules the User Is Playing
        #model = GameModel(game_model_data)
        #instance = model.load_game_instance()
        instance = game_model_data
        if request.user.is_authenticated():
            cur_vals = Game_Instance.objects.get(user=request.user).data
            return render(request, self.template_name, {'game': instance, 'vals': cur_vals})
        else:
            start_vals = game_model_data['new_game']
            return render(request, self.template_name, {'game': instance, 'vals': start_vals})

    def post(self, request):
        #import pdb; pdb.set_trace()
        if 'building' in request.POST:
            pass  # purchase_building
        elif 'upgrade' in request.POST:
            pass  # purchase_upgrade
        elif 'clicker' in request.POST:
            game_rules = Clicker_Game.objects.all()[0].game_data
            game_instance = Game_Instance.objects.get(user=request.user)
            game_instance.data['clicks'] += game_rules['clicked']
            game_instance.save()
            return JsonResponse({'vals': game_instance.data})
