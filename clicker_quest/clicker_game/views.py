from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from clicker_game.models import Game_Instance

# Create your views here.


class GameView(View):
    template_name = 'base.html'

    def get(self, request):
        the_game = Game_Instance.objects.get(user=self.request.user)
        return render(request, self.template_name, {'the_game': the_game})
