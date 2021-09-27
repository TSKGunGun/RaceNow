import factory
from place.models import Place
from account.tests.factories import UserFactory

class PlaceFactory(factory.django.DjangoModelFactory):
    
    owner = factory.SubFactory(UserFactory)
    name = factory.sequence(lambda n: u'place_%d' % n)
    address = factory.Faker("address", locale="ja_JP")
    url = factory.Faker("uri")


    class Meta:
        model = Place