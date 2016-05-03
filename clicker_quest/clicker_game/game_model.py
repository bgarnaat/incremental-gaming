# coding=utf-8
from clicker_game.models import Clicker_Game
from django.core.exceptions import ObjectDoesNotExist


class GameModel(object):
    def __init__(self, game_data):
        """
        Load the game from game model information.

        May raise a ValueError if the model does not validate.
        """
        self.data = game_data
        self.instance = self.generate_instance_data()

    def generate_instance_data(self):
        """Ouput a dictonary containing all the information of this certain game.

        Has all inital values.
        Converted to JSON by view to be used by front end."""
        game_state = {'resources': {}, 'buildings': {}, 'upgrades': {}}
        import pdb; pdb.set_trace()
        for resource in self.data['resources']:
            game_state['resources'][resource] = {}
            state_rescoure = game_state['resources'][resource]
            data_rescourse = self.data['resources'][resource]
            state_rescoure['description'] = data_rescourse['description']
            state_rescoure['owned'] = 0
            state_rescoure['income'] = 0
            state_rescoure['maximum'] = data_rescourse['maximum']

        for building in self.data['buildings']:
            game_state['buildings'][building] = {}
            state_buildings = game_state['buildings'][building]
            state_buildings['description'] = building['description']
            data_building = self.data['buildings'][building]
            state_buildings['owned'] = 0
            state_buildings['cost'] = data_building['cost']
            state_buildings['cost10'] = data_building['cost'] * 10
            state_buildings['income'] = data_building['income']

        for upgrade in self.data['upgrades']:
            game_state['upgrades'][upgrade] = {}
            state_upgrade = game_state['upgrades'][upgrade]
            data_upgrade = self.data['upgrades'][upgrade]
            state_upgrade['description'] = data_upgrade['description']
            state_upgrade['cost'] = data_upgrade['cost']
            state_upgrade['unlock'] = data_upgrade['unlock']

        return game_state

    def get_current_state(self, game_state, game_state_time, current_time):
        """
        Read a game state object, advance it forwards in time to the current time, and return the
        (modified game state, and data to pass to the client) in a tuple
        """

        return game_state, {"for client": "information"}

    def purchase_building(self, game_state, game_state_time, current_time, building_name, number_purchased):
        """
        Read a game state object, advance it forwards in time to the current time, purchase the specified
        buildings if possible, and return the (modified game state, and data to pass to the client) in a tuple
        """
        return game_state, {"for client": "information"}

    def purchase_upgrade(self, game_state, game_state_time, current_time, upgrade_name):
        """
        Read a game state object, advance it forwards in time to the current time, purchase the specified
        upgrade if possible, and return the (modified game state, and data to pass to the client) in a tuple
        """
        return game_state, {"for client": "information"}
