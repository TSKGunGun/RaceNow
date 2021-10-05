from django.http import response
from django.test import TestCase
from account.models import Organizer
from race.models import Race, RaceStatus, RaceType
from .factories import RaceFactory,EntrantFactory,Lap_Factory,Entrant_Member_Factory
from account.tests.factories import UserFactory, OrganizerFactory
from django.urls import reverse

class Race_Model_Test(TestCase):
    fixtures = ['race_default.json']
    
    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
    
    def test_get_regulationsetup(self):
        self.client.logout()
        self.client.force_login(self.user)

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )
        response = self.client.get(reverse("regulations_setup", kwargs={"pk":self.race.id}))

        self.assertEqual(response.status_code, 200)

    def test_get_regulationsetup_notlogin(self):
        self.client.logout()

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )
        response = self.client.get(reverse("regulations_setup", kwargs={"pk":self.race.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_get_regulationsetup_notMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )
        response = self.client.get(reverse("regulations_setup", kwargs={"pk":self.race.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_get_regulationsetup_notMatchStatus(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        invalid_statuses = [RaceStatus.RACE_STATUS_ENTRY, RaceStatus.RACE_STATUS_HOLD, RaceStatus.RACE_STATUS_END, RaceStatus.RACE_STATUS_CANCEL]
        
        for status in invalid_statuses:
            with self.subTest(status=status):
                self.race.status = RaceStatus.objects.get(id=status)
                self.race.save()
                self.assertEqual(Race.objects.get(pk=self.race.id).status.id, status )
                response = self.client.get(reverse("regulations_setup", kwargs={"pk":self.race.id}))
                self.assertNotEqual(response.status_code, 200)

        self.race.status = RaceStatus.objects.get(id=RaceStatus.RACE_STATUS_DEFAULT)
        self.race.save()
        response = self.client.get(reverse("regulations_setup", kwargs={"pk":self.race.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_regulationsetup(self):
        self.client.logout()
        self.client.force_login(self.user)

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )

        params = {
            "is_teamrace" : False,
            "teammember_count_min" : 1,
            "teammember_count_max" : 1,
            "is_heat" : False,
            "heat_count" : 1
        }

        self.assertFalse(Race.objects.get(pk=self.race.id).is_regulationsetuped)
        response = self.client.post(reverse("regulations_setup", kwargs={"pk":self.race.id}), params)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Race.objects.get(pk=self.race.id).is_regulationsetuped)

    def test_post_regulationsetup_notlogin(self):
        self.client.logout()

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )

        params = {
            "is_teamrace" : False,
            "teammember_count_min" : 1,
            "teammember_count_max" : 1,
            "is_heat" : False,
            "heat_count" : 1
        }
        response = self.client.post(reverse("regulations_setup", kwargs={"pk":self.race.id}), params)

        self.assertNotEqual(response.status_code, 200)

    def test_post_regulationsetup_notMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        self.assertEqual(Race.objects.get(pk=self.race.id).status.id, RaceStatus.RACE_STATUS_DEFAULT )

        params = {
            "is_teamrace" : False,
            "teammember_count_min" : 1,
            "teammember_count_max" : 1,
            "is_heat" : False,
            "heat_count" : 1
        }
        response = self.client.post(reverse("regulations_setup", kwargs={"pk":self.race.id}), params)

        self.assertNotEqual(response.status_code, 200)

    def test_post_regulationsetup_notMatchStatus(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        invalid_statuses = [RaceStatus.RACE_STATUS_ENTRY, RaceStatus.RACE_STATUS_HOLD, RaceStatus.RACE_STATUS_END, RaceStatus.RACE_STATUS_CANCEL]        
        
        params = {
            "is_teamrace" : False,
            "teammember_count_min" : 1,
            "teammember_count_max" : 1,
            "is_heat" : False,
            "heat_count" : 1
        }
        
        for status in invalid_statuses:
            with self.subTest(status=status):
                self.race.status = RaceStatus.objects.get(id=status)
                self.race.save()
                self.assertEqual(Race.objects.get(pk=self.race.id).status.id, status )


                response = self.client.post(reverse("regulations_setup", kwargs={"pk":self.race.id}), params)
                self.assertNotEqual(response.status_code, 200)

        self.race.status = RaceStatus.objects.get(id=RaceStatus.RACE_STATUS_DEFAULT)
        self.race.save()
        response = self.client.post(reverse("regulations_setup", kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 302)

