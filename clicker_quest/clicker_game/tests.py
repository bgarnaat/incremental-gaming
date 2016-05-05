from django.test import TestCase
from django.conf import settings
from clicker_game.models import ClickerGame, GameInstance
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
        self.game = ClickerGame(owner=self.user, game_data={'click': 5},
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
        self.game = ClickerGame(owner=self.user, game_data=u'JSON goes here.',
                                name=u'Test Game')
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
