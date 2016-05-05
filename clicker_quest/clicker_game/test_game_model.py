# coding=utf-8
from datetime import datetime, timedelta
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
        except ValueError as ex:
            self.assertIn(message, ex.args[0])
        else:
            self.assertFalse("validation did not fail")

    def validate_ok(self):
        validate_game_model(self.game)

    def test_non_dict_model(self):
        with self.assertRaises(ValueError):
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
                    'unlock': {'upgrades': ["gas mining"]},
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
                    'name': "gas mining",
                    'unlock': {'buildings': {"extractor": 2}},
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

    def test_initial_state(self):
        self.instance.calculate_values()
        self.assertEqual(
            self.instance.save_state_json(),
            self.game.new_game
        )
        self.assertEqual(
            self.instance.client_state_json(),
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

    # todo test game mechanics
