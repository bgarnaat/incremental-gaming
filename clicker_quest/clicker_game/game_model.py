# coding=utf-8


class GameModel(object):
    def __init__(self, game_model_data):
        """
        Load the game from game model information.

        May raise a ValueError if the model does not validate.
        """
        self.game_data = game_model_data

    def report_full_game_state(self):
        """
        Outputs complete information about the given game state for the front end to display.

        Used for full update of the front end when the page is loaded.
        """
        return game_state, {"for client": "information"}

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
