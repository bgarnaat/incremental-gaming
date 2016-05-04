from django.test import TestCase, Client
from django.conf import settings
from clicker_game.models import Clicker_Game, Game_Instance
import factory
import datetime
# Create your tests here.


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
        self.game = Clicker_Game(owner=self.user, game_data={'click': 5},
                                 name=u'Test Game')
        self.game.save()
        # Test the game is owned by a user and can easily be retrieved
        self.assertEqual(self.game.owner, self.user)
        self.assertEqual(self.game.game_data['click'], 5)
        self.assertEqual(self.game.name, u'Test Game')
        self.assertIsInstance(self.game.modified, datetime.datetime)
        self.assertIsInstance(self.game.created, datetime.datetime)


class GameInstanceTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.game = Clicker_Game(owner=self.user, game_data=u'JSON goes here.',
                                 name=u'Test Game')
        self.game.save()

    def test_make_game_instance(self):
        """Test An Game Instance can be made."""
        self.game1 = Game_Instance(user=self.user, game=self.game,
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
        self.game_json = {
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
                            'multiplier': 2
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
        self.db_json = {
                'resources': {
                    'quests': 316
                },
                'buildings': {'Quest Maker': 2},
                'upgrades': []
            }
        self.game_rules = Clicker_Game(owner=self.user, game_data=self.game_json, name='Quest Clicker')
        self.game_rules.save()
        self.game_instance = Game_Instance(user=self.user, game=self.game_rules, data=self.db_json)
        self.game_instance.save()

    def test_get_request(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/test/')
