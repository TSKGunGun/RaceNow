import account
import factory
from factory import fuzzy
from race.models import Race, Entrant, Entrant_Member, RaceType, Category
import string
from datetime import datetime, timedelta
from account.tests.factories import OrganizerFactory
from place.tests.factories import PlaceFactory

class CategoryFactory(factory.django.DjangoModelFactory):
    name = "オフロードレース"

    class Meta:
        model = Category
        django_get_or_create = ("name",)

class RaceTypeFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    name = "クロスカントリー"
    
    class Meta:
        model = RaceType
        django_get_or_create = ("name",)

class RaceFactory(factory.django.DjangoModelFactory):
    organizer = factory.SubFactory(OrganizerFactory)
    name = fuzzy.FuzzyText(prefix="racename_", length=30)
    racetype = factory.SubFactory(RaceTypeFactory)
    event_date = fuzzy.FuzzyDate(start_date=datetime.today() + timedelta(days=1), end_date=datetime.today() + timedelta(days=100))
    place = factory.SubFactory(PlaceFactory)

    class Meta:
        model = Race

class EntrantFactory(factory.django.DjangoModelFactory):

    race = factory.SubFactory(RaceFactory)
    team_name = fuzzy.FuzzyText(length=20, chars=string.ascii_letters, prefix="team_")
    num = fuzzy.FuzzyText(length=5, chars="0123456789")    

    class Meta:
        model = Entrant

class Entrant_Member_Factory(factory.django.DjangoModelFactory):    
    belonging = factory.SubFactory(EntrantFactory)
    name = factory.Faker("name", locale="ja_JP")

    class Meta:
        model = Entrant_Member
