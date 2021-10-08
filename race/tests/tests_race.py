from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer
from place.models import Place
from race.models import Race, RaceStatus, RaceType
from race.forms import EventDateValidator
from .factories import RaceFactory,EntrantFactory,Lap_Factory,Entrant_Member_Factory
from account.tests.factories import UserFactory, OrganizerFactory
from django.utils import timezone
from datetime import datetime, timedelta, tzinfo, date
from unittest.mock import patch

class Race_Model_Test(TestCase):
    fixtures = ['race_default.json']
    
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
            event_date = timezone.now(),
            url = ""
        )

        self.assertEqual(Race.objects.count(), 1)

class Race_CreateView_Test(TestCase):
    fixtures = ['race_default.json']

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
            "url" : "",
            "note" : ""
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
            "url" : "",
            "note" : ""
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
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : date.today().strftime("%Y-%m-%d"),
            "url" : "",
            "note" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        
        self.assertTrue(Race.objects.exists())
        self.assertEqual(response.status_code, 302)

    def test_validation_date_notinput(self):
        params = {
            "name":"test_race",
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : "",
            "url" : "",
            "note" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        
        self.assertFalse(Race.objects.exists())
        self.assertEqual(response.status_code, 200)
    
    def test_validation_eventdate_befordate(self):
        params = {
            "name":"test_race",
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : (timezone.now()-timedelta(days=1)).strftime("%Y-%m-%d"),
            "url" : "",
            "note" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        self.assertFalse(Race.objects.exists())
    
    def test_validation_eventdate_afterdate(self):
        params = {
            "name":"test_race",
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : (date.today()+timedelta(days=1)).strftime("%Y-%m-%d"),
            "url" : "",
            "note" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        
        self.assertTrue(Race.objects.exists())
        self.assertEqual(response.status_code, 302)

    def test_validation_eventdate_badformat(self):
        params = {
            "name":"test_race",
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : (date.today()+timedelta(days=1)).strftime("%Y/%m/%d"),
            "url" : "",
            "note" : ""
        }
        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        
        self.assertFalse(Race.objects.exists())
        self.assertEqual(response.status_code, 200)

    def test_craterace_notecheck(self):
        params = {
            "name":"test_race",
            "place" : self.place.id,
            "category" : 1,
            "racetype" : 1,
            "event_date" : date.today().strftime("%Y-%m-%d"),
            "url" : "",
            "note" : "SampleNote"
        }

        self.org.members.add(self.user)
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertFalse(Race.objects.exists())
        response = self.client.post(f'/organizer/{self.org.id}/createrace', params)
        self.assertTrue(Race.objects.exists())

        self.assertEqual(Race.objects.first().note, "SampleNote" )

class EventDateValidationTest(TestCase):
    def test_samedate(self):
        testdate = timezone.now().today().date()
        EventDateValidator(testdate)

    def test_beforedate(self):
        testdate = (timezone.now()-timedelta(days=1)).date()

        with self.assertRaises(ValidationError, msg="開催日に過去の日付は設定できません。"):
            EventDateValidator(testdate)

    def test_afterdate(self):
        testdate = (timezone.now() + timedelta(days=1)).date()
        EventDateValidator(testdate)

class Race_StartTest(TestCase):
    fixtures = ['race_default.json']

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
        self.org.members.add(self.user)

        self.place = Place.objects.create(
            owner = self.user,
            name = "test_place",
            address = "test_place_address"
        )

        self.race = Race.objects.create(
            organizer = self.org,
            place = self.place,
            name = "test_race",
            racetype = RaceType.objects.get(pk=1),
            event_date = timezone.now(),
            url = ""
        )

    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_changeRaceStatus(self, _mock_now):
        startdatetime = datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc)
        
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(self.race.start_at, None )

        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_HOLD)
        self.assertEqual(race.start_at,  startdatetime)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url=f"/race/{self.race.id}/detail", status_code=302, target_status_code=200)

    def test_getrequest(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f"/race/{self.race.id}/startrace")

        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_notlogin(self):
        self.client.logout()
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 302)
    
    def test_notmember(self):
        self.client.logout
        other_usr = get_user_model().objects.create_user(
            username = "testuser2",
            password = "password"
        )
        self.client.force_login(other_usr)
        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 403)


class Race_FixedReglation(TestCase):
    fixtures = ['race_default.json']

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
        self.org.members.add(self.user)

        self.place = Place.objects.create(
            owner = self.user,
            name = "test_place",
            address = "test_place_address"
        )

        self.race = Race.objects.create(
            organizer = self.org,
            place = self.place,
            name = "test_race",
            racetype = RaceType.objects.get(pk=1),
            event_date = timezone.now(),
            url = ""
        )

    def test_changeRaceStatus(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_HOLD)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url=f"/race/{self.race.id}/detail", status_code=302, target_status_code=200)

    def test_getrequest(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f"/race/{self.race.id}/startrace")

        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_notlogin(self):
        self.client.logout()
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 302)
    
    def test_notmember(self):
        self.client.logout
        other_usr = get_user_model().objects.create_user(
            username = "testuser2",
            password = "password"
        )
        self.client.force_login(other_usr)
        response = self.client.post(f"/race/{self.race.id}/startrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 403)


class fiexedreguration_View_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        
        self.user = get_user_model().objects.first()

    def test_changeRaceStatus(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/fixedregulation")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_ENTRY)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url=f"/race/{self.race.id}/detail", status_code=302, target_status_code=200)

    def test_getrequest(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f"/race/{self.race.id}/fixedregulation")

        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_notlogin(self):
        self.client.logout()
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/fixedregulation")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 302)
    
    def test_notmember(self):
        self.client.logout
        other_usr = UserFactory()
        self.client.force_login(other_usr)
        response = self.client.post(f"/race/{self.race.id}/fixedregulation")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 403)


class finishRace_View_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        
        self.user = get_user_model().objects.first()

    def test_changeRaceStatus(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/finishrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_END)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url=f"/race/{self.race.id}/detail", status_code=302, target_status_code=200)

    def test_getrequest(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f"/race/{self.race.id}/finishrace")

        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 405)
    
    def test_notlogin(self):
        self.client.logout()
        self.assertEqual(self.race.status.id, RaceStatus.RACE_STATUS_DEFAULT)

        response = self.client.post(f"/race/{self.race.id}/finishrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 302)
    
    def test_notmember(self):
        self.client.logout
        other_usr = UserFactory()
        self.client.force_login(other_usr)
        response = self.client.post(f"/race/{self.race.id}/finishrace")

        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.status.id, RaceStatus.RACE_STATUS_DEFAULT)
        self.assertEqual(response.status_code, 403)

