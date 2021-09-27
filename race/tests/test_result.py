from django.test import TestCase
from race.models import Race, RaceStatus, Category, RaceType
from place.models import Place
from account.models import Organizer
from .factories import RaceFactory, EntrantFactory, Entrant_Member_Factory
from django.utils import timezone

# Create your tests here.
class Race_Model_Test(TestCase):
    fixtures = ['race_default.json']
    
    def setUp(self):
        pass
    
    def test_factories(self):
        self.race = RaceFactory()
        ent1 = EntrantFactory(race=self.race)
        m1 = Entrant_Member_Factory(belonging=ent1)

        ent2 = EntrantFactory(race=self.race)
        m2 = Entrant_Member_Factory(belonging=ent2)

        self.assertEqual(self.race.entrant_set.count(), 2 )
