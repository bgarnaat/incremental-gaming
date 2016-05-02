from django.test import TestCase
from django.conf import settings
import factory

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


class GameTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_game_exists(self):
        """Test a game can be made with the proper properties."""
        import pdb; pdb.set_trace()