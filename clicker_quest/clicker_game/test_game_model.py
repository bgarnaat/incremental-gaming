# coding=utf-8
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase

from clicker_game.game_model import (
    validate_game_model,
    seconds_to_fast_forward,
    FULL_SPEED_TIME,
    DECAY_TIME,
)


def cost(base, factor, owned, buy):
    return sum(base * factor ** n for n in range(owned, owned + buy))


class GameModelValidationTest(TestCase):
    def setUp(self):
        self.game = {
            'name': "game",
            'description': "a game",
            'resources': [],
            'buildings': [],
            'upgrades': [],
            'new_game': {},
        }

    def dont_validate(self, message, ):
        try:
            validate_game_model(self.game)
        except ValidationError as ex:
            self.assertIn(message, ex.args[0])
        else:
            self.assertFalse("validation did not fail")

    def validate_ok(self):
        validate_game_model(self.game)

    def test_non_dict_model(self):
        with self.assertRaises(ValidationError):
            validate_game_model("not a dict")

    def test_non_list_resources(self):
        self.game['resources'] = "not a list"
        self.dont_validate("must all be lists")

    def test_non_list_buildings(self):
        self.game['buildings'] = "not a list"
        self.dont_validate("must all be lists")

    def test_non_list_upgrades(self):
        self.game['upgrades'] = "not a list"
        self.dont_validate("must all be lists")

    def test_non_dict_new_game(self):
        self.game['new_game'] = "not a dict"
        self.dont_validate("New game state must be a json object")

    def test_missing_keys_model(self):
        self.game.pop('upgrades')
        self.dont_validate("Missing or extra keys")
    
    def test_extra_keys_model(self):
        self.game['invalid_extra_key'] = 5
        self.dont_validate("Missing or extra keys")

    def test_unnamed_resource(self):
        self.game['resources'].append({'maximum': 100})
        self.dont_validate("Missing key: name")

    def test_unnamed_building(self):
        self.game['buildings'].append({'cost': {}, 'cost_factor': 2})
        self.dont_validate("Missing key: name")

    def test_unnamed_upgrade(self):
        self.game['upgrades'].append({'cost': {}, 'buildings': {}})
        self.dont_validate("Missing key: name")
    
    def test_overload_resources(self):
        entry = {'name': "abc"}
        self.game['resources'].append(entry)
        self.validate_ok()
        self.game['resources'].append(entry)
        self.dont_validate("Two resources share the same name")
    
    def test_overload_buildings(self):
        entry = {'name': "abc", 'cost': {}, 'cost_factor': 2}
        self.game['buildings'].append(entry)
        self.validate_ok()
        self.game['buildings'].append(entry)
        self.dont_validate("Two buildings share the same name")
    
    def test_overload_upgrades(self):
        entry = {'name': "abc", 'cost': {}}
        self.game['upgrades'].append(entry)
        self.validate_ok()
        self.game['upgrades'].append(entry)
        self.dont_validate("Two upgrades share the same name")

    def test_valid_resources(self):
        self.game['resources'].extend([
            {'name': "abc"},
            {'name': "def", 'maximum': 5},
        ])
        self.validate_ok()
    
    def test_nonnumeric_resource_max(self):
        self.game['resources'].append(
            {'name': "abc", 'maximum': "not a number"}
        )
        self.dont_validate("non-numeric maximum")

    def test_non_dict_unlock(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': [6],
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("Unlock must be a json object")

    def test_unlock_extra_keys(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {'invalid key': 1},
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("Extra values in unlock")

    def test_unlock_buildings_non_dict(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {
                    'buildings': "not a dict"
                },
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("must be a json object")

    def test_unlock_invalid_building(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {
                    'buildings': {"def": 1}
                },
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("references nonexistent building")

    def test_unlock_non_numeric_building_number(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {
                    'buildings': {"abc": "not a number"}
                },
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("Non-numeric number of required buildings")

    def test_unlock_upgrades_non_list(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {
                    'upgrades': "not a list"
                },
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("must be a list")

    def test_unlock_invalid_upgrade(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'unlock': {
                    'upgrades': ["nonexistent"]
                },
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.dont_validate("references nonexistent upgrade")

    def test_good_unlock(self):
        self.game['buildings'].extend([
            {  # with just buildings in unlock
                'name': "abc",
                'unlock': {
                    'buildings': {"abc": 1},
                },
                'cost': {},
                'cost_factor': 2,
            },
            {  # with just upgrades
                'name': "def",
                'unlock': {
                    'upgrades': ["upgrade"],
                },
                'cost': {},
                'cost_factor': 2,
            },
            {  # with both
                'name': "ghi",
                'unlock': {
                    'buildings': {"abc": 1},
                    'upgrades': ["upgrade"],
                },
                'cost': {},
                'cost_factor': 2,
            },
        ])
        self.game['upgrades'].append(
            {  # required upgrade
                'name': "upgrade",
                'cost': {},
            }
        )
        self.validate_ok()

    def test_building_without_cost(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost_factor': 2
            }
        )
        self.dont_validate("Missing key: cost")

    def test_building_with_non_dict_cost(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': ["not a dict"],
                'cost_factor': 2,
            }
        )
        self.dont_validate("must be a json object")

    def test_building_with_invalid_cost_resource(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {"nonexistent": 1},
                'cost_factor': 2,
            }
        )
        self.dont_validate("nonexistent resource")

    def test_building_with_non_numeric_cost_amount(self):
        self.game['resources'].append(
            {'name': 'minerals'}
        )
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {"minerals": "not a number"},
                'cost_factor': 2,
            }
        )
        self.dont_validate("Non-numeric resource")

    def test_building_with_non_numeric_cost_factor(self):
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {},
                'cost_factor': "not a number",
            }
        )
        self.dont_validate("Non-numeric cost factor")

    def test_building_with_invalid_income(self):
        self.game['resources'].append(
            {'name': "a"}
        )
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {"a": 1},
                'cost_factor': 2,
                'income': {"a": 1, "b": 2},
            }
        )
        self.dont_validate("nonexistent resource")

    def test_building_with_invalid_storage(self):
        self.game['resources'].append(
            {
                'name': "a",
                'maximum': 100,
            }
        )
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {"a": 1},
                'cost_factor': 2,
                'storage': "not a dict",
            }
        )
        self.dont_validate("must be a json object")

    def test_building_with_storage_for_unlimited_resource(self):
        self.game['resources'].append(
            {'name': "a"}
        )
        self.game['buildings'].append(
            {
                'name': "abc",
                'cost': {"a": 1},
                'cost_factor': 2,
                'storage': {"a": 10},
            }
        )
        self.dont_validate("storage for an unlimited resource")

    def test_upgrade_with_invalid_unlock(self):
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': "not a dict"
            }
        )
        self.dont_validate("must be a json object")

    def test_upgrade_without_cost(self):
        self.game['upgrades'].append(
            {
                'name': "abc",
                'unlock': {
                    'upgrades': ["abc"]
                },
            }
        )
        self.dont_validate("Missing key: cost")

    def test_upgrade_with_invalid_cost(self):
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': "not a dict",
                'unlock': {
                    'upgrades': ["abc"]
                },
            }
        )
        self.dont_validate("must be a json object")

    def test_upgrade_affects_nonexistent_building(self):
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "nonexistent": {
                        'income': {}
                    }
                }
            }
        )
        self.dont_validate("affects nonexistent building")

    def test_upgrade_affects_invalid_building_property(self):
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'what is this': {}
                    },
                },
            }
        )
        self.dont_validate("Unknown effect specified")

    def test_upgrade_building_cost_nonexistent_resource(self):
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "nonexistent": {
                                'multiplier': .5,
                            },
                        },
                    },
                },
            }
        )
        self.dont_validate("affects cost for nonexistent resource")

    def test_upgrade_non_dict_modifier(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": "not a dict"
                        },
                    },
                },
            }
        )
        self.dont_validate("Modifier of a value must be a json object")

    def test_upgrade_invalid_modifier_key(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": {
                                'invalid modification': 5,
                            },
                        },
                    },
                },
            }
        )
        self.dont_validate("Unknown key in value modifier")

    def test_upgrade_modifier_non_numeric_value(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": {
                                'multiplier': "not a number",
                            },
                        },
                    },
                },
            }
        )
        self.dont_validate("Non-numeric modifier value")

    def test_upgrade_building_income_nonexistent_resource(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
                'income': {
                    "minerals": 1,
                }
            }
        )
        self.game['upgrades'].append(
            {
                'name': "abc",
                'cost': {},
                'unlock': {
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'income': {
                            "minerals": {'multiplier': 2},
                            "vespene gas": {'multiplier': 2},
                        },
                    },
                },
            }
        )
        self.dont_validate("Upgrade affects income for nonexistent resource")

    def test_valid_upgrades(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
                'income': {
                    "minerals": 1,
                }
            }
        )
        self.game['upgrades'].extend([
            {
                'name': "abc",
                'cost': {"minerals": 1},
                'unlock': {
                    'buildings': {"building": 1},
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": {'multiplier': .5},
                        },
                        'income': {
                            "minerals": {'multiplier': 2},
                        },
                    },
                },
            },
            {
                'name': "def",
                'cost': {"minerals": 100},
                'unlock': {
                    'buildings': {"building": 10},
                    'upgrades': ["abc"],
                },
                'buildings': {
                    "building": {
                        'income': {
                            "minerals": {'multiplier': 2},
                        },
                    },
                },
            },
            {
                'name': "ghi",
                'cost': {"minerals": 10000},
                'unlock': {
                    'buildings': {"building": 100},
                    'upgrades': ["def"],
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": {'multiplier': .5},
                        },
                    },
                },
            },
        ])
        self.validate_ok()

    def test_new_game_extra_key(self):
        self.game['new_game'] = {
            'unknown': {1: 1},
        }
        self.dont_validate("Invalid key in new game state")

    def test_new_game_invalid_resources(self):
        self.game['new_game'] = {
            'resources': "not a dict"
        }
        self.dont_validate("Resource amounts must be a json object")

    def test_new_game_non_dict_buildings(self):
        self.game['new_game'] = {
            'buildings': "not a dict"
        }
        self.dont_validate("building counts must be a json object")

    def test_new_game_non_list_upgrades(self):
        self.game['new_game'] = {
            'upgrades': "not a list"
        }
        self.dont_validate("Upgrades value in new game state is not a list")

    def test_new_game_nonexistent_building(self):
        self.game['new_game'] = {
            'buildings': {"nonexistent": 1}
        }
        self.dont_validate("Nonexistent building in new game state")

    def test_new_game_non_numeric_building_count(self):
        self.game['buildings'].append(
            {'name': "abc", 'cost': {}, 'cost_factor': 2}
        )
        self.game['new_game'] = {
            'buildings': {
                "abc": "not a number"
            }
        }
        self.dont_validate("Non-numeric number of buildings in new game")

    def test_new_game_nonexistent_upgrade(self):
        self.game['new_game'] = {
            'upgrades': ["nonexistent"]
        }
        self.dont_validate("Nonexistent upgrade in new game")

    def test_valid_new_game(self):
        self.game['resources'].append(
            {'name': "minerals"}
        )
        self.game['buildings'].append(
            {
                'name': "building",
                'cost': {},
                'cost_factor': 2,
                'income': {
                    "minerals": 1,
                }
            }
        )
        self.game['upgrades'].extend([
            {
                'name': "abc",
                'cost': {"minerals": 1},
                'unlock': {
                    'buildings': {"building": 1},
                },
                'buildings': {
                    "building": {
                        'cost': {
                            "minerals": {'multiplier': .5},
                        },
                        'income': {
                            "minerals": {'multiplier': 2},
                        },
                    },
                },
            },
        ])
        self.game['new_game'] = {
            'resources': {"minerals": 1},
            'buildings': {"building": 1},
            'upgrades': ["abc"],
        }
        self.validate_ok()


class FastForwardTestCase(TestCase):
    def test_negative_time(self):
        self.assertEqual(
            seconds_to_fast_forward(timedelta(seconds=-1000)),
            0.0
        )

    def test_full_speed(self):
        self.assertEqual(
            seconds_to_fast_forward(timedelta(seconds=FULL_SPEED_TIME)),
            FULL_SPEED_TIME
        )

    def test_partial_speed(self):
        test_time = FULL_SPEED_TIME + DECAY_TIME / 2
        self.assertLess(
            seconds_to_fast_forward(timedelta(seconds=test_time)),
            test_time
        )

    def test_time_stops_after_decay(self):
        self.assertEqual(
            seconds_to_fast_forward(timedelta(seconds=FULL_SPEED_TIME + DECAY_TIME)),
            seconds_to_fast_forward(timedelta(seconds=FULL_SPEED_TIME + DECAY_TIME * 3))
        )


class GameModelTestCase(TestCase):
    def setUp(self):
        self.game = validate_game_model({
            'name': "game",
            'description': "a game",
            'resources': [
                {
                    'name': "minerals",
                },
                {
                    'name': "gas",
                    'maximum': 100.0,
                },
            ],
            'buildings': [
                {
                    'name': "miner",
                    'cost': {"minerals": 10.0},
                    'cost_factor': 1.1,
                    'income': {"minerals": 5.0},
                },
                {
                    'name': "extractor",
                    'unlock': {'upgrades': ["gas extraction"]},
                    'cost': {'minerals': 50.0},
                    'cost_factor': 1.5,
                    'income': {"gas": 5.0},
                    'storage': {"gas": 10.0},
                },
                {
                    'name': "warehouse",
                    'unlock': {'buildings': {"extractor": 1}},
                    'cost': {
                        "minerals": 3.0,
                        "gas": 2.0,
                    },
                    'cost_factor': 2.0,
                    'storage': {
                        "gas": 20.0,
                    },
                },
            ],
            'upgrades': [
                {
                    'name': "gas extraction",
                    'unlock': {'buildings': {"miner": 2}},
                    'cost': {"minerals": 60.0},
                },
                {
                    'name': "extractor efficiency",
                    'unlock': {'buildings': {"extractor": 4}},
                    'cost': {
                        "minerals": 200.0,
                        "gas": 100.0,
                    },
                    'buildings': {
                        "extractor": {
                            'cost': {"minerals": {'multiplier': .5}},
                            'income': {"gas": {'multiplier': 2.0}},
                        },
                    },
                },
            ],
            'new_game': {'resources': {"minerals": 16.0}}
        })
        self.time = datetime(2000, 1, 1)
        self.instance = self.game.load_game_instance(self.game.new_game, self.time)
        self.maxDiff = None

    def test_acquire_resource(self):
        self.instance.calculate_values()
        self.instance.acquire_resource("gas", 1.0)
        self.assertEqual(
            self.instance.save_state_json(),
            {'resources': {"minerals": 16.0, "gas": 1.0}}
        )

    def test_acquire_resource_over_max(self):
        self.instance.calculate_values()
        self.instance.acquire_resource("gas", 1e20)
        self.assertEqual(self.instance.resources["gas"].owned, 100.0)

    def test_acquire_storage(self):
        self.instance.calculate_values()
        self.instance.acquire_storage("gas", 42.0)
        self.assertEqual(self.instance.resources["gas"].maximum, 142.0)
        self.instance.acquire_resource("gas", 1e20)
        self.assertEqual(self.instance.resources["gas"].owned, 142.0)

    def test_acquire_income(self):
        self.instance.calculate_values()
        self.instance.acquire_income("gas", 42.0)
        self.assertEqual(self.instance.resources["gas"].income, 42.0)

    def test_acquire_building(self):
        self.instance.acquire_building("warehouse", 1)
        self.assertEqual(self.instance.buildings["warehouse"].owned, 1)

    def test_buildings_increase_in_cost(self):
        self.instance.calculate_values()
        self.assertEqual(
            self.instance.cost_of_building("miner", 1),
            {"minerals": 10.0}
        )
        self.instance.acquire_building("miner", 1)
        self.instance.calculate_values()
        self.assertEqual(
            self.instance.cost_of_building("miner", 1),
            {"minerals": 11.0}
        )

    def test_buildings_affect_income(self):
        self.instance.acquire_building("miner", 1)
        self.instance.calculate_values()
        self.assertEqual(self.instance.resources["minerals"].income, 5.0)

    def test_buildings_affect_storage(self):
        self.instance.acquire_building("warehouse", 1)
        self.instance.calculate_values()
        self.assertEqual(self.instance.buildings["warehouse"].owned, 1)
        self.assertEqual(self.instance.resources["gas"].maximum, 120.0)

    def test_acquire_upgrade(self):
        self.instance.acquire_upgrade("extractor efficiency")
        self.assertIn("extractor efficiency", self.instance.upgrades)

    def test_upgrades_affect_buildings(self):
        self.instance.acquire_building("extractor", 1)
        self.instance.calculate_values()
        self.assertEqual(
            self.instance.cost_of_building("extractor", 1),
            {"minerals": 75.0}
        )
        self.assertEqual(
            self.instance.buildings["extractor"].income,
            {"gas": 5.0}
        )
        self.assertEqual(
            self.instance.resources["gas"].income,
            5.0
        )
        self.instance.acquire_upgrade("extractor efficiency")
        self.instance.calculate_values()
        self.assertEqual(
            self.instance.cost_of_building("extractor", 1),
            {"minerals": 75.0 / 2}
        )
        self.assertEqual(
            self.instance.buildings["extractor"].income,
            {"gas": 10.0}
        )
        self.assertEqual(
            self.instance.resources["gas"].income,
            10.0
        )

    def test_initial_state(self):
        save, client = self.instance.get_current_state(self.time)
        self.assertEqual(
            save,
            self.game.new_game
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 16.0,
                        'maximum': None,
                        'income': 0.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 0,
                        'cost': {"minerals": 10.0},
                        'cost10': {"minerals": cost(10, 1.1, 0, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_do_nothing(self):
        save, client = self.instance.get_current_state(self.time + timedelta(seconds=3600))
        self.assertEqual(
            save,
            self.game.new_game
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 16.0,
                        'maximum': None,
                        'income': 0.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 0,
                        'cost': {"minerals": 10.0},
                        'cost10': {"minerals": cost(10, 1.1, 0, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_purchase_building_fail_too_many(self):
        save, client = self.instance.purchase_building(self.time, "miner", 10)
        # nothing has changed
        self.assertEqual(
            save,
            self.game.new_game
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 16.0,
                        'maximum': None,
                        'income': 0.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 0,
                        'cost': {"minerals": 10.0},
                        'cost10': {"minerals": cost(10, 1.1, 0, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_purchase_building_fail_not_unlocked(self):
        self.instance.calculate_values()
        self.instance.acquire_resource("minerals", 1000.0)
        save, client = self.instance.purchase_building(self.time, "extractor", 1)
        # nothing has changed
        self.assertEqual(
            save,
            {'resources': {"minerals": 1016.0}}
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 1016.0,
                        'maximum': None,
                        'income': 0.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 0,
                        'cost': {"minerals": 10.0},
                        'cost10': {"minerals": cost(10, 1.1, 0, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_purchase_building_success(self):
        save, client = self.instance.purchase_building(self.time, "miner", 1)
        # now we have 1 miner
        self.assertEqual(
            save,
            {
                'resources': {"minerals": 6.0},
                'buildings': {"miner": 1},
            }
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 6.0,
                        'maximum': None,
                        'income': 5.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 1,
                        'cost': {"minerals": cost(10, 1.1, 1, 1)},
                        'cost10': {"minerals": cost(10, 1.1, 1, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_purchase_building_and_wait(self):
        self.instance.purchase_building(self.time, "miner", 1)
        save, client = self.instance.get_current_state(self.time + timedelta(seconds=10))
        # now we have 1 miner
        self.assertEqual(
            save,
            {
                'resources': {"minerals": 56.0},  # 5 minerals/second
                'buildings': {"miner": 1},
            }
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 56.0,
                        'maximum': None,
                        'income': 5.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 1,
                        'cost': {"minerals": cost(10, 1.1, 1, 1)},
                        'cost10': {"minerals": cost(10, 1.1, 1, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [],
            }
        )

    def test_make_upgrade_available(self):
        self.instance.purchase_building(self.time, "miner", 1)
        save, client = self.instance.purchase_building(self.time + timedelta(seconds=10), "miner", 1)
        # with two miners the "gas extraction" upgrade should be unlocked
        self.assertEqual(
            save,
            {
                'resources': {"minerals": 45.0},  # 5 minerals/second
                'buildings': {"miner": 2},
            }
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': 45.0,
                        'maximum': None,
                        'income': 10.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 2,
                        'cost': {"minerals": cost(10, 1.1, 2, 1)},
                        'cost10': {"minerals": cost(10, 1.1, 2, 10)},
                        'income': {"minerals": 5.0},
                    },
                ],
                'upgrades': [
                    {
                        'name': "gas extraction",
                        'description': "",
                        'owned': False,
                        'cost': {"minerals": 60},
                    },
                ],
            }
        )

    def test_buy_upgrade(self):
        self.instance.purchase_building(self.time, "miner", 1)
        self.instance.purchase_building(
            self.time + timedelta(seconds=10),
            "miner", 1
        )
        self.instance.purchase_upgrade(
            self.time + timedelta(seconds=20),
            "gas extraction"
        )
        save, client = self.instance.purchase_building(
            self.time + timedelta(seconds=120),
            "miner", 2
        )
        # we don't own any extractors but they should be available
        self.assertNotIn("extractor", save['buildings'])
        self.assertIn("extractor", (x['name'] for x in client['buildings']))
        # warehouse is not unlocked yet either
        self.assertNotIn("warehouse", (x['name'] for x in client['buildings']))
        # now buy 1 extractor
        save, client = self.instance.purchase_building(
            self.time + timedelta(seconds=120),
            "extractor", 1
        )
        expected_minerals = (
            16 +                        # starting minerals
            (-10) +                     # first miner purchased
            5.0*10 +                    # income from 0-10 seconds
            (-11) +                     # second miner purchased
            10.0*10 +                   # income from 10-20 seconds
            (-60) +                     # cost of gas extraction
            10.0*100 +                  # income from 20-120 seconds
            (-cost(10, 1.1, 2, 2)) +    # cost of 3rd and 4th miners
            (-50.0)                     # cost of extractor
        )
        self.assertEqual(
            save,
            {
                'resources': {"minerals": expected_minerals},  # 5 minerals/second
                'buildings': {"miner": 4, "extractor": 1},
                'upgrades': ["gas extraction"],
            }
        )
        self.assertEqual(
            client,
            {
                'resources': [
                    {
                        'name': "minerals",
                        'description': "",
                        'owned': expected_minerals,
                        'maximum': None,
                        'income': 20.0,
                    },
                    {
                        'name': "gas",
                        'description': "",
                        'owned': 0.0,
                        'maximum': 110.0,
                        'income': 5.0,
                    },
                ],
                'buildings': [
                    {
                        'name': "miner",
                        'description': "",
                        'owned': 4,
                        'cost': {"minerals": cost(10, 1.1, 4, 1)},
                        'cost10': {"minerals": cost(10, 1.1, 4, 10)},
                        'income': {"minerals": 5.0},
                    },
                    {
                        'name': "extractor",
                        'description': "",
                        'owned': 1,
                        'cost': {"minerals": cost(50, 1.5, 1, 1)},
                        'cost10': {"minerals": cost(50, 1.5, 1, 10)},
                        'income': {"gas": 5.0},
                    },
                    {
                        'name': "warehouse",
                        'description': "",
                        'owned': 0,
                        'cost': {"minerals": 3.0, "gas": 2.0},
                        'cost10': {
                            "minerals": cost(3.0, 2.0, 0, 10),
                            "gas": cost(2.0, 2.0, 0, 10),
                        },
                        'income': {},
                    },
                ],
                'upgrades': [
                    {
                        'name': "gas extraction",
                        'description': "",
                        'owned': True,
                        'cost': {"minerals": 60.0},
                    },
                ],
            }
        )

    def test_do_not_double_buy_upgrade(self):
        self.instance.purchase_building(self.time, "miner", 1)
        self.instance.purchase_building(
            self.time + timedelta(seconds=10),
            "miner", 1
        )
        self.instance.purchase_upgrade(
            self.time + timedelta(seconds=1000),
            "gas extraction"
        )
        current_minerals = self.instance.resources["minerals"].owned
        # make sure we have enough money to buy it again
        self.assertGreaterEqual(current_minerals, self.game.upgrades["gas extraction"].cost["minerals"])
        # attempt to purchase upgrade again
        self.instance.purchase_upgrade(
            self.time + timedelta(seconds=1000),
            "gas extraction"
        )
        # money should not have gone down
        self.assertEqual(current_minerals, self.instance.resources["minerals"].owned)
