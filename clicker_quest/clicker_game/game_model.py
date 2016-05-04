# coding=utf-8
from collections import OrderedDict


"""
Provides modular incremental game model functionality.

validate_game_model(json_data):
    Validate a game model information blob.
    This should only need to be called the first time a game model json description is stored
    to make sure it is ok.

GameModel(json_data):
    Describes a game model.

    new_game:
        Attribute containing the starting game-state value for new games
        played with this model.
        
    load_game_instance(instance_data, instance_time):
        Returns a new GameInstance object that can perform actions on a game instance being
        played with this game model. Warranty does not cover giving instances that belong to
        another game.

GameInstance:
    Calculates the state of a game being played. Get this from GameModel.load_game_instance()

    get_current_state(current_time):
        Fast forward this game instance from the time it was loaded with to the given current
        time. Returns two values in a tuple: a new game instance json data dict that can be stored
        in the database for the state at the current time, and another json data dict of
        information to send to the javascript client.

    purchase_building(current_time, building_name, number_purchased):
        Like get_current_state, but also attempts to purchase some buildings at the current
        time.

    purchase_upgrade(current_time, upgrade_name):
        Again like get_current_state, but also attempts to purchase an upgrade at the current time.


    ~~~ Other methods that probably aren't needed outside this module: ~~~

    save_state_json():
        This makes the save state data object that the main three methods return

    client_state_json():
        Likewise for the client info object
"""


class Dicted(object):
    """Basic python object that we can hang easy attributes off of.
    This should be much easier than constantly referencing dictionaries."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def validate_game_model(json_data):
    """Validate a game model data wad and return the GameModel object if the game model is OK,
    or raise a ValueError if there is a problem with the game model (some descriptive
    information should be in the .args of the error)."""
    try:
        if not isinstance(json_data, dict):
            raise ValueError("Game model must be a json object with keys and values")

        difference = set(json_data).symmetric_difference(
            {'name', 'description', 'resources', 'buildings', 'upgrades'}
        )
        if difference:
            raise ValueError("Missing or extra keys in game model description", difference)

        model = GameModel(json_data)

        # noinspection PyShadowingNames
        def validate_resource_amounts(cost_data):
            for resource_name, amount in cost_data.values():
                if resource_name not in model.resources:
                    raise ValueError("Nonexistent resource specified", resource_name)
                if not isinstance(amount, (int, float)):
                    raise ValueError("Non-numeric resource amount", resource_name, amount)

        # noinspection PyShadowingNames
        def validate_unlock(unlock):
            if unlock is ():
                return
            if not isinstance(unlock, dict):
                raise ValueError("Unlock must be an object with keys and values")
            if not all(x in ('buildings', 'upgrades') for x in unlock):
                raise ValueError("Extra values in unlock", unlock)
            if unlock:
                for building_name, number in unlock['buildings']:
                    if building_name not in model.buildings:
                        raise ValueError("Unlock references nonexistent building", building_name)
                    if not isinstance(number, (int, float)):
                        raise ValueError("Non-numeric required number of buildings in unlock", number)
                for upgrade_name in unlock['upgrades']:
                    if upgrade_name not in model.upgrades:
                        raise ValueError("Unlock references nonexistent upgrade", upgrade_name)

        if len(json_data['resources']) != len(model.resources):
            raise ValueError("Two resources share the same name")
        if len(json_data['buildings']) != len(model.buildings):
            raise ValueError("Two buildings share the same name")
        if len(json_data['upgrades']) != len(model.upgrades):
            raise ValueError("Two upgrades share the same name")

        for resource in model.resources.values():
            if not isinstance(resource.maximum, (int, float, type(None))):
                raise ValueError("A resource has a non-numerical maximum")

        for building in model.buildings.values():
            validate_unlock(building.unlock)
            validate_resource_amounts(building.cost)
            if not isinstance(building.cost_factor, (int, float)):
                raise ValueError("Non-numeric cost factor for building", building.name, building.cost_factor)
            validate_resource_amounts(building.income)
            validate_resource_amounts(building.storage)
            for resource_name in building.storage:
                if building.resources[resource_name].maximum is None:
                    raise ValueError("Building has storage for an unlimited resource", building.name, resource_name)

        for upgrade in model.upgrades.values():
            validate_unlock(upgrade.unlock)
            validate_resource_amounts(upgrade.cost)
            for building_name, effects in upgrade().buildings:
                if building_name not in model.buildings:
                    raise ValueError("Upgrade affects cost of nonexistent building", upgrade.name, building_name)
                for effect_type in effects:
                    if effect_type not in ('cost', 'income'):
                        raise ValueError(
                            "Unknown effect specified for upgrade",
                            upgrade.name, building_name, effect_type
                        )
                if 'cost' in effects:
                    for resource_name, multiplier in effects['cost']:
                        if resource_name not in model.resources:
                            raise ValueError(
                                "Upgrade affects cost for nonexistent resource",
                                upgrade.name, building_name, resource_name
                            )
                        if not isinstance(multiplier, (int, float)):
                            raise ValueError(
                                "Non-numeric building cost multiplier in an upgrade",
                                upgrade.name, building_name, resource_name, multiplier
                            )
                if 'income' in effects:
                    for resource_name, income in effects['cost']:
                        if resource_name not in model.resources:
                            raise ValueError(
                                "Upgrade affects cost for nonexistent resource",
                                upgrade.name, building_name, resource_name
                            )
                        if not isinstance(income, (int, float)):
                            raise ValueError(
                                "Non-numeric building income multiplier in an upgrade",
                                upgrade.name, building_name, resource_name, income
                            )

            for key in model.new_game:
                if key not in ('resources', 'buildings', 'upgrades'):
                    raise ValueError("Invalid key in new game state", key)
                if 'resources' in model.new_game:
                    validate_resource_amounts(model.new_game['resources'])
                if 'buildings' in model.new_game:
                    for building_name, number in model.new_game['buildings'].items():
                        if building_name not in model.buildings:
                            raise ValueError("Nonexistent building in new game state", building_name)
                        if not isinstance(number, (int, float)):
                            raise ValueError(
                                "Non-numeric number of buildings in new game state",
                                building_name, number
                            )
                if 'upgrades' in model.new_game:
                    if not isinstance(model.new_game['upgrades'], list):
                        raise ValueError("Upgrades value in new game state is not a list")
                    for upgrade_name in model.new_game['upgrades']:
                        if upgrade_name not in model.upgrades:
                            raise ValueError("Nonexistent upgrade in new game state", upgrade_name)

    except ValueError:
        raise
    except KeyError as ex:
        raise ValueError("Missing key", ex.args)
    except AttributeError as ex:
        raise ValueError("Wrong type of value somewhere", ex.args)

    return model


class GameModel(object):
    def __init__(self, json_data):
        """
        Load the game from game model information.

        May raise a ValueError if the model does not validate.
        """
        # game info
        self.name = json_data['name']
        self.description = json_data['description']

        # resources
        self.resources = OrderedDict()
        for resource in json_data['resources']:
            resource = Dicted(
                name=self.resources['name'],
                description=resource.get('description', ""),
                maximum=resource.get('maximum'),
            )
            self.resources[resource.name] = resource

        # buildings
        self.buildings = OrderedDict()
        for building in json_data['buildings']:
            building = Dicted(
                name=building['name'],
                description=building.get('description', ""),
                unlock=building.get('unlock', ()),
                cost=building['cost'],
                cost_factor=building['cost_factor'],
                income=building.get('income', {}),
                storage=building.get('storage', {}),
            )
            self.buildings[building.name] = building

        # upgrades
        self.upgrades = OrderedDict()
        for upgrade in json_data['upgrades']:
            upgrade = Dicted(
                name=upgrade['name'],
                description=upgrade.get('description', ""),
                unlock=upgrade.get('unlock', ()),
                cost=upgrade['cost'],
                buildings=upgrade.get('buildings', {}),
            )
            self.upgrades[upgrade.name] = upgrade

        # new game game-state
        self.new_game = json_data['new_game']

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
        if (
            building_name in self.model.buildings and
            self.pay_cost(self.cost_of_building(building_name, number_to_buy=number_purchased))
        ):
            self.acquire_building(building_name, number_purchased)
            self.calculate_values()
        return self.save_state_json(), self.client_state_json()

    def purchase_upgrade(self, current_time, upgrade_name):
        """
        Read a game state object, advance it forwards in time to the current time, purchase the specified
        upgrade if possible, and return the (modified game state, and data to pass to the client) in a tuple
        """
        self.fast_forward(current_time)
        if (
            upgrade_name in self.model.buildings and
            self.pay_cost(self.model.upgrades[upgrade_name].cost)
        ):
            self.upgrades.add(upgrade_name)
            self.calculate_values()
        return self.save_state_json(), self.client_state_json()

    def save_state_json(self):
        """Return the save state json object for this game state, boiled down to its minimum"""
        result = {}
        if self.resources:
            result['resources'] = {name: resource.owned for name, resource in self.resources.items()}
        if self.buildings:
            result['buildings'] = {name: building.owned for name, building in self.buildings.items()}
        if self.upgrades:
            result['upgrades'] = list(self.upgrades)
        return result

    def client_state_json(self):
        """
        Return the information about the game state suitable for the client side JS to render
        the page we want the user to see
        """
        result = {
            'resources': [],
            'buildings': [],
            'upgrades': [],
        }
        # resources
        if self.resources:
            for resource in self.model.resources.values():
                owned = self.resources.get(resource.name)
                if owned and (owned.owned or owned.income):
                    result['resources'].append({
                        'name': resource.name,
                        'description': resource.description,
                        'owned': owned.owned,
                        'income': owned.income,
                        'maximum': owned.maximum,
                    })

        # buildings
        for building in self.model.buildings.values():
            owned = building.name in self.buildings and self.buildings[building.name].owned or 0
            income = owned and self.buildings[building.name].income or building.income
            if owned or self.requirement_is_met(building.unlock):
                result['buildings'].append({
                    'description': building.description,
                    'owned': owned,
                    'cost': self.cost_of_building(building.name, 1),
                    'cost10': self.cost_of_building(building.name, 10),
                    'income': income,
                })

        # upgrades
        for upgrade in self.model.upgrades.values():
            if upgrade.name in self.upgrades or self.requirement_is_met(upgrade.unlock):
                result['upgrades'].append({
                    'description': upgrade.description,
                    'owned': upgrade.name in self.upgrades,
                    'cost': upgrade.cost,
                })

        return result

    def calculate_values(self):
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

        # reset resources maximums and incomes
        for name, resource in self.resources.items():
            resource.income = 0.0
            resource.maximum = self.model.resources[name].maximum

        # calculate total storage and income right now
        for building in self.buildings.values():
            for resource, storage in building.storage.items():
                self.acquire_storage(resource, storage * building.owned)
            for resource, income in building.income.items():
                self.resources[resource].income += income * building.owned

    def acquire_resource(self, resource_name, amount):
        """Add an amount of a resource to the state"""
        if resource_name not in self.resources:
            self.resources[resource_name] = Dicted(owned=0.0, maximum=self.model.resources[resource_name].maximum)
        self.resources[resource_name].owned += amount

    def acquire_storage(self, resource_name, storage):
        """Add an amount of storage for a resource to the state"""
        if resource_name not in self.resources:
            self.resources[resource_name] = Dicted(
                owned=0.0,
                income=0.0,
                maximum=self.model.resources[resource_name].maximum
            )
        self.resources[resource_name].maximum += storage

    def acquire_income(self, resource_name, income):
        """Add an amount of income to the calculated state"""
        if resource_name not in self.resources:
            self.resources[resource_name] = Dicted(
                owned=0.0,
                income=0.0,
                maximum=self.model.resources[resource_name].maximum
            )
        self.resources[resource_name].income += income

    def acquire_building(self, building_name, number):
        """Add a number of buildings to the state"""
        if building_name not in self.buildings:
            self.buildings[building_name] = Dicted(owned=0)
        self.buildings[building_name].owned += number

    def acquire_upgrade(self, upgrade_name):
        """Add an upgrade to this game state"""
        self.upgrades.add(upgrade_name)

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
            if not all(
                building in self.buildings and self.buildings[building].owned >= count
                for building, count in unlock['buildings']
            ):
                return False
        if 'upgrades' in unlock:
            if not all(
                upgrade in self.upgrades
                for upgrade in unlock['upgrades']
            ):
                return False
        return True

    def cost_of_building(self, building_name, number_to_buy=1):
        """Calculate the cost of purchasing a certain number of a building"""
        if building_name not in self.buildings:
            raise KeyError(building_name)
        building = self.buildings[building_name]
        result = {resource: 0.0 for resource in building.cost}
        for resource, amount in building.cost.items():
            for n in range(building.owned, building.owned + number_to_buy):
                result[resource] += amount * self.model.buildings[building_name].cost_factor ** n
        return result

    def cost_is_affordable(self, cost):
        """Determine whether a cost is currently affordable"""
        return all(
            resource in self.resources and self.resources[resource].owned >= amount
            for resource, amount in cost.items()
        )

    def pay_cost(self, cost):
        """If a cost is affordable, pay the cost and return True. Otherwise, return False."""
        if not self.cost_is_affordable(cost):
            return False
        for resource, amount in cost.items():
            self.resources[resource].owned -= amount
        return True
