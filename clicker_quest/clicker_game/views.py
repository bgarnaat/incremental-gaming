from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from clicker_game.models import Game_Instance, Clicker_Game
import clicker_game.game_model as gm
import datetime

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
        current_time = datetime.datetime.now()
        current_game = Clicker_Game.objects.all()[0]
        game_model_data = current_game.game_data
        game_model = gm.GameModel(game_model_data)
        if request.user.is_authenticated():
            db_instance = Game_Instance.objects.get(user=request.user,
                                                    game=current_game)
            game_instance = game_model.load_game_instance(db_instance.data,
                                                          db_instance.modified)
            db_json, front_end_json = game_instance.get_current_state(
                current_time)
            db_instance.data = db_json
            db_instance.modified = current_time
            db_instance.save()
            if request.is_ajax():
                game = front_end_json
                return JsonResponse(game)
            else:
                return render(request, self.template_name, {'game': front_end_json})
        else:
            # TODO: Render A New Game.
            pass

    def post(self, request):
        # Set up the current game instance
        current_time = datetime.datetime.now()
        current_game = Clicker_Game.objects.all()[0]
        game_model_data = current_game.game_data
        game_model = gm.GameModel(game_model_data)
        db_instance = Game_Instance.objects.get(user=request.user,
                                                game=current_game)
        game_instance = game_model.load_game_instance(db_instance.data,
                                                      db_instance.modified)

        if 'building' in request.POST:
            building_name = request.POST.get('name')
            number_purchased = request.POST.get('number_purchased')
            db_json, front_end_json = game_instance.purchase_building(
                current_time, building_name, number_purchased)
        elif 'upgrade' in request.POST:
            upgrade_name = request.POST.get('name')
            db_json, front_end_json = game_instance.purchase_upgrade(
                current_time, upgrade_name)
        # Save new info to the database, return the new values to the front end
        db_instance.data = db_json
        db_instance.modified = current_time
        db_instance.save()
        game = front_end_json
        return JsonResponse(game)
