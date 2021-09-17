from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer
from place.models import Place
from race.models import Race, RaceStatus, RaceType

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

        
    def test_createRace(self):
        self.assertEqual(Race.objects.count(), 0)

        rtype = RaceType.objects.get(pk=1)

        race = Race.objects.create(
            organizer = self.org,
            place = self.place,
            name = "test_race",
            racetype = rtype,
            url = ""
        )

        self.assertEqual(Race.objects.count(), 1)

class Race_CreateView_Test(TestCase):
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

    def test_getpage_notlogin(self):
        self.client.logout()
        response = self.client.get(f'/organizer/{self.org.id}/createrace')

        self.assertEqual(response.status_code, 302)

    def test_getpage_loginend_notmember(self):
        user2 = get_user_model().objects.create_user(
            username = "username",
            password = "password"
        )
        org2 = Organizer.objects.create(
            owner = user2,
            name = "test_org2",
            email_address = "test@example.com"
        )
        org2.members.add(user2)
        
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.get(f'/organizer/{org2.id}/createrace')

        self.assertEqual(response.status_code, 403)
    
    def test_getpage_loginend_member(self):
        user2 = get_user_model().objects.create_user(
            username = "username",
            password = "password"
        )
        
        self.client.logout()
        self.client.force_login(user2)
        response = self.client.get(f'/organizer/{self.org.id}/createrace')
        self.assertEqual(response.status_code, 403)

        self.org.members.add(user2)
        response = self.client.get(f'/organizer/{self.org.id}/createrace')
        self.assertEqual(response.status_code, 200)
    
    def test_postpage_notlogin(self):
        params = {
            "organizer" : self.org.id,
            "place" : 1,
            "category" : 1,
            "racetype" : 1,
            "url" : ""
        }
        
        self.client.logout()
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        self.assertEqual(response.status_code, 302)

    def test_postpage_logined_notmember(self):
        params = {
            "organizer" : self.org.id,
            "place" : 1,
            "category" : 1,
            "racetype" : 1,
            "url" : ""
        }
        
        user2 = get_user_model().objects.create_user(
            username = "username",
            password = "password"
        )
        org2 = Organizer.objects.create(
            owner = user2,
            name = "test_org2",
            email_address = "test@example.com"
        )

        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.post(f'/organizer/{org2.id}/createrace', params)
        self.assertEqual(response.status_code, 403)

    def test_postpage_create(self):
        params = {
            "name":"test_race",
            "organizer" : self.org.id,
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "url" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        
        self.assertTrue(Race.objects.exists())
        self.assertEqual(response.status_code, 302)

    def test_postpage_invalid(self):
        pass