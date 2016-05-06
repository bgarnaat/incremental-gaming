from django.test import TestCase, Client
from django.conf import settings
from clicker_game.models import ClickerGame, GameInstance
from clicker_game.game_model import GameModel
import factory
import datetime
# Create your tests here.

TEST_GAME = {
    'name': 'Test Game',
    'description': 'Click thing to make quest',
    'resources': [{
        'name': 'quests',
        'description': 'The All Important Quest',
        'maximum': 999
    }],
    'buildings': [{
        'name': 'Quest Maker',
        'description': 'Makes Quests',
        'unlock': {},
        'cost': {
            'quests': 10
        },
        'cost_factor': .5,
        'income': {'quests': 1},
        'storage': {}
    }],
    'upgrades': [{
        'name': 'fleagal power',
        'description': 'Harness The Power of <0>',
        'unlock': {
            'buildings': {
                'Quest Maker': 5
            }
        },
        'cost': {'quests': 200},
        'buildings': {
            'Quest Maker': {
                'cost': {
                    "quests": {
                        'multiplier': 2
                    }
                },
                'income': {
                    'quests': {'multiplier': 2}
                }
            }
        }
    }],
    'new_game': {
        'resources': {
            'quests': 50
        },
        'buildings': {},
        'upgrades': []
    }
}


class UserFactory(factory.django.DjangoModelFactory):
    """Test using factory for user model.."""

    class Meta:
        """Establish User model as the product of this factory."""

        model = settings.AUTH_USER_MODEL
        django_get_or_create = ('username',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = factory.LazyAttribute(
        lambda object: ''.join((object.first_name, object.last_name)))
    password = factory.PostGenerationMethodCall('set_password', 'password')


class ClickerGameTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_game_exists(self):
        """Test a game can be made with the proper properties."""
        self.game = ClickerGame(owner=self.user, game_data=TEST_GAME,
                                name='Test Game')
        self.game.save()
        # Test the game is owned by a user and can easily be retrieved
        self.assertEqual(self.game.owner, self.user)
        self.assertEqual(self.game.game_data['description'], 'Click thing to make quest')
        self.assertEqual(self.game.name, 'Test Game')
        self.assertIsInstance(self.game.modified, datetime.datetime)
        self.assertIsInstance(self.game.created, datetime.datetime)


class GameValidationTest(TestCase):
    def test_invalid_game_fails_to_save(self):
        user = UserFactory.create()
        game = ClickerGame(
            owner=user,
            game_data=['invalid game'],
            name="invalid game"
        )
        with self.assertRaises(ValueError):
            game.save()


class GameInstanceTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.game = ClickerGame(owner=self.user, game_data=TEST_GAME,
                                name="Test Game")
        self.game.save()

    def test_make_game_instance(self):
        """Test An Game Instance can be made."""
        self.game1 = GameInstance(user=self.user, game=self.game,
                                  data={'clicks': 34})
        self.game1.save()
        self.assertEqual(self.game1.user, self.user)
        self.assertEqual(self.game1.game, self.game)
        self.assertEqual(self.game1.data['clicks'], 34)
        self.assertIsInstance(self.game1.modified, datetime.datetime)
        self.assertIsInstance(self.game1.created, datetime.datetime)


class MainViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.game_json = TEST_GAME
        self.db_json = {
                'resources': {
                    'quests': 316
                },
                'buildings': {'Quest Maker': 2},
                'upgrades': []
            }
        self.game_rules = ClickerGame(owner=self.user, game_data=self.game_json, name='Quest Clicker')
        self.game_rules.save()
        self.game_instance = GameInstance(user=self.user, game=self.game_rules, data=self.db_json)
        self.game_instance.save()

    def test_get_request_html(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/test/')
        self.assertTemplateUsed(response, 'index.html')
        self.assertIsInstance(response.context['game'], dict)

    def test_get_request_ajax(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.json())

    def test_post_building(self):
        c = Client()
        c.force_login(self.user)
        response = c.post(
            '/test/',
            {'building': True, 'name': 'a building', 'number_purchased': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.json())

    def test_post_update(self):
        c = Client()
        c.force_login(self.user)
        response = c.post(
            '/test/',
            {'upgrade': True, 'name': 'a upgrade'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.json())

    def test_post_junk(self):
        """Test to see if a general ajax still returns json correctly."""
        c = Client()
        c.force_login(self.user)
        response = c.post(
            '/test/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.json())

