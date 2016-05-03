# coding=utf-8


class Dicted(object):
    """Basic python object that we can hang easy attributes off of.
    This should be much easier than constantly referencing dictionaries."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class GameModel(object):
    def __init__(self, data):
        """
        Load the game from game model information.

        May raise a ValueError if the model does not validate.
        """
        self.description = data.pop('description')
        # resources
        self.resources = {
            name: Dicted(
                description=resource.get('description', ""),
                maximum=resource.get('maximum'),
            )
            for name, resource in data.pop('resources').items()
        }
        # buildings
        self.buildings = {
            name: Dicted(
                description=building.get('description', ""),
                unlock=building.get('unlock', ()),
                cost=building['cost'],
                cost_factor=building['cost_factor'],
                income=building.get('income', {}),
                storage=building.get('storage', {}),
            )
            for name, building in data.pop('buildings').items()
        }
        # upgrades
        self.upgrades = {
            name: Dicted(
                description=upgrade.get('description', ""),
                unlock=upgrade.get('unlock', ()),
                cost=upgrade['cost'],
                buildings=upgrade.get('buildings', {}),
            )
            for name, upgrade in data.pop('upgrades').items()
        }
        # new game game-state
        self.new_game = data.pop('new_game')

    def load_game_instance(self, game_instance, game_instance_time):
        return GameInstance(self, game_instance, game_instance_time)


def seconds_to_fast_forward(time):
    """
    Calculate the effective number of seconds to fast forward for a given wait period.

    Accepts a timedelta and returns a float.
    """
    return time.total_second()  # todo: long idle times should result in less effective time passed


class GameInstance(object):
    def __init__(self, model, instance_data, instance_time):
        self.model = model
        self.time = instance_time
        self.resources = instance_data.get('resources') or {}
        self.buildings = instance_data.get('buildings') or {}
        self.upgrades = set(instance_data.get('upgrades')) or set()
        # convert to python objects
        self.resources = {name: Dicted(owned=count) for name, count in self.resources.items()}
        self.buildings = {name: Dicted(owned=count) for name, count in self.buildings.items()}

    def get_current_state(self, current_time):
        """
        Read a game state object, advance it forwards in time to the current time, and return the
        (modified game state, and data to pass to the client) in a tuple
        """
        self.fast_forward(current_time)
        return self.save_state_json(), self.client_state_json()

    def purchase_building(self, current_time, building_name, number_purchased):
        """
        Read a game state object, advance it forwards in time to the current time, purchase the specified
        buildings if possible, and return the (modified game state, and data to pass to the client) in a tuple
        """
        self.fast_forward(current_time)
        # todo: attempt purchase of a building
        return self.save_state_json(), self.client_state_json()

    def purchase_upgrade(self, current_time, upgrade_name):
        """
        Read a game state object, advance it forwards in time to the current time, purchase the specified
        upgrade if possible, and return the (modified game state, and data to pass to the client) in a tuple
        """
        self.fast_forward(current_time)
        # todo: attempt purchase of an upgrade
        return self.save_state_json(), self.client_state_json()

    def save_state_json(self):
        """Return the save state json object for this game state, boiled down to its minimum"""
        result = {}
        if self.resources:
            result['resources'] = {name: resource.owned for name, resource in self.resources.items()}
        if self.buildings:
            result['buildings'] = {name: building.owned for name, building in self.buildings.items()}
        if self.upgrades:
            result['upgrades'] = self.upgrades.copy()
        return result

    def client_state_json(self):
        """
        Return the information about the game state suitable for the client side JS to render
        the page we want the user to see
        """
        return {"todo": "show some stuff to the client"}  # TODO

    def calculate_values(self):
        for name, resource in self.resources.items():
            resource.income = 0.0
            if self.model.resources[name].maximum is not None:
                resource.maximum = self.model.resources[name].maximum

        # calculate resource incomes per building type
        for name, building in self.buildings.items():
            # incomes are per resource
            building.income = self.model.buildings[name].incomes.copy()
            building.multiplier = {resource: 1.0 for resource in building.income}
            building.cost = self.model.buildings[name].cost.copy()

        # calculate upgrades
        for upgrade in self.upgrades:
            # effects on buildings
            for building, effects in self.model.upgrades[upgrade].buildings:
                # cost multipliers
                if 'cost' in effects:
                    for resource, cost_multiplier in effects['cost']:
                        building.cost[resource] *= cost_multiplier
                # income multipliers
                if 'income' in effects:
                    for resource, income_multiplier in effects['income']:
                        building.income[resource] *= income_multiplier
        # calculate total storage and income right now
        for building in self.buildings.values():
            for resource, storage in building.storage.items():
                self.resources[resource].maximum += storage * building.owned
            for resource, income in building.income.items():
                self.resources[resource].income += income * building.owned

    def fast_forward(self, current_time):
        """Fast forward the time of the game state to the given time"""
        self.calculate_values()
        seconds = seconds_to_fast_forward(current_time - self.time)
        for resource in self.resources.values():
            resource.owned = min(resource.owned + resource.income * seconds, resource.maximum)
        self.time = current_time

    def requirement_is_met(self, unlock):
        """
        Take a data block from the game model that specifies the required buildings and upgrades
        to unlock a specific thing and return True if those requirements are met (False otherwise).
        """
        if 'buildings' in unlock:
            if not all(self.buildings[building].owned >= count for building, count in unlock['buildings']):
                return False
        if 'upgrades' in unlock:
            if not all(upgrade in self.upgrades for upgrade in unlock['upgrades']):
                return False
        return True
