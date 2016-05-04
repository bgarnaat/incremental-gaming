# coding=utf-8
from django.test import TestCase

from clicker_game.game_model import GameModel, GameInstance, validate_game_model


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

    def dont_validate(self):
        with self.assertRaises(ValueError):
            validate_game_model(self.game)

    def validate_ok(self):
        validate_game_model(self.game)

    def test_non_dict_model(self):
        with self.assertRaises(ValueError):
            validate_game_model(["not a dict"])
    
    def test_missing_keys_model(self):
        self.game.pop('upgrades')
        self.dont_validate()
    
    def test_extra_keys_model(self):
        self.game['invalid_extra_key'] = 5
        self.dont_validate()

    def test_unnamed_resource(self):
        self.game['resources'].append({1: "unnamed"})
        self.dont_validate()

    def test_unnamed_building(self):
        self.game['buildings'].append({1: "unnamed"})
        self.dont_validate()

    def test_unnamed_upgrade(self):
        self.game['upgrades'].append({1: "unnamed"})
        self.dont_validate()
    
    def test_overload_resources(self):
        entry = {'name': "abc"}
        self.game['resources'].append(entry)
        self.validate_ok()
        self.game['resources'].append(entry)
        self.dont_validate()
    
    def test_overload_buildings(self):
        entry = {'name': "abc", 'cost': {}}
        self.game['buildings'].append(entry)
        self.validate_ok()
        self.game['buildings'].append(entry)
        self.dont_validate()
    
    def test_overload_upgrades(self):
        entry = {'name': "abc", 'cost': {}}
        self.game['upgrades'].append(entry)
        self.validate_ok()
        self.game['upgrades'].append(entry)
        self.dont_validate()

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
        self.dont_validate()

    def test_non_dict_unlock(self):
        self.game['buildings'].append(
            {'name': "abc", 'unlock': [6], 'cost': {}}
        )
        self.dont_validate()

    def test_unlock_extra_keys(self):
        pass  # todo

    def test_unlock_invalid_building(self):
        pass  # todo

    def test_unlock_non_numeric_building_number(self):
        pass  # todo

    def test_unlock_invalid_upgrade(self):
        pass  # todo

    def test_good_unlock(self):
        pass  # todo

    def test_building_without_cost(self):
        pass  # todo

    def test_building_with_non_dict_cost(self):
        pass  # todo

    def test_building_with_invalid_cost_resource(self):
        pass  # todo

    def test_building_with_non_numeric_cost_amount(self):
        pass  # todo

    def test_building_with_non_numeric_cost_factor(self):
        pass  # todo

    def test_building_with_invalid_income(self):
        pass  # todo

    def test_building_with_invalid_storage(self):
        pass  # todo

    def test_building_with_storage_for_unlimited_resource(self):
        pass  # todo

    def test_upgrade_with_invalid_unlock(self):
        pass  # todo

    def test_upgrade_without_cost(self):
        pass  # todo

    def test_upgrade_with_invalid_cost(self):
        pass  # todo

    def test_upgrade_affects_nonexistent_building(self):
        pass  # todo

    def test_upgrade_affects_invalid_building_property(self):
        pass  # todo

    def test_upgrade_building_cost_nonexistent_resource(self):
        pass  # todo

    def test_upgrade_non_dict_modifier(self):
        pass  # todo

    def test_upgrade_invalid_modifier_key(self):
        pass  # todo

    def test_upgrade_modifier_non_numeric_value(self):
        pass  # todo

    def test_upgrade_building_income_nonexistent_resource(self):
        pass  # todo

    def test_valid_upgrades(self):
        pass  # todo

    def test_new_game_non_dict(self):
        pass  # todo

    def test_new_game_invalid_resources(self):
        pass  # todo

    def test_new_game_nonexistent_building(self):
        pass  # todo

    def test_new_game_non_numeric_building_count(self):
        pass  # todo

    def test_new_game_nonexistent_upgrade(self):
        pass  # todo

    def test_valid_new_game(self):
        pass  # todo

    # todo calculation tests
