from os import stat_result
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer
from place.models import Place
from race.models import Race, RaceStatus, RaceType
from django.utils import timezone

class Race_Model_Test(TestCase):
    fixtures = ['race_default.json', 'race_status_default.json']
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username = "test_user",
            password = "password"
        )

        self.org = Organizer.objects.create(
            owner = self.user,
            name = "test_organizer",
            email_address = "test@example.com"
        )

        self.place = Place.objects.create(
            owner = self.user,
            name = "test_place",
            address = "test_place_address"
        )

        self.race = Race.objects.create(
            organizer = self.org,
            event_date = timezone.now(),
            name = "test_race",
            place = self.place,
            status = RaceStatus.objects.get(pk=1)
        )
