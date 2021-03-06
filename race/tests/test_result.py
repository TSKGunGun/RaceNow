import json
from time import timezone
from django.contrib.auth import get_user_model
from django.http import response
from django.test import TestCase
from django.urls.base import reverse
from django.views.decorators.http import require_POST
import pytz
from account.models import Organizer
from race.models import Race, Lap, Entrant, RaceStatus
from .factories import RaceFactory, EntrantFactory, Entrant_Member_Factory, Lap_Factory
from account.tests.factories import UserFactory, OrganizerFactory
from datetime import datetime, timedelta,time
from django.utils import timezone
from unittest.mock import patch


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

    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_getResult_ent2(self, _mock_now):
        self.race = RaceFactory()
        startdatetime = datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc)

        ent1 = EntrantFactory(race=self.race)
        ent2 = EntrantFactory(race=self.race)

        _mock_now.return_value = startdatetime + timedelta(minutes=5)
        Lap_Factory(entrant=ent1)

        _mock_now.return_value = startdatetime + timedelta(minutes=8)
        Lap_Factory(entrant=ent2)
        
        _mock_now.return_value = startdatetime + timedelta(minutes=15, seconds=1)
        Lap_Factory(entrant=ent2)

        _mock_now.return_value = startdatetime + timedelta(minutes=15)
        Lap_Factory(entrant=ent1)

        #ent1 15分 2周 ent2 15分1秒 2周
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result.first().id, ent1.id)
        self.assertEqual(result[1].id, ent2.id)

        #ent1 15分 2周 ent2 18分 3周
        _mock_now.return_value = startdatetime + timedelta(minutes=18)
        Lap_Factory(entrant=ent2)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result.first().id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)

        #ent1 18分1秒 3周 ent2 18分 3周
        _mock_now.return_value = startdatetime + timedelta(minutes=18, seconds=1)
        Lap_Factory(entrant=ent1)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result.first().id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)
    
    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_getResult_ent5(self, _mock_now):
        self.race = RaceFactory()
        startdatetime = datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc)

        ent1 = EntrantFactory(race=self.race)
        ent2 = EntrantFactory(race=self.race)
        ent3 = EntrantFactory(race=self.race)
        ent4 = EntrantFactory(race=self.race)
        ent5 = EntrantFactory(race=self.race)

        #エラーが発生しなければよい
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result.count(), 5)
        
        #ent1 5分 1周 ent2 4分59秒 1周 ent3 5分1秒 1周 ent4 6分 1周 ent5 5分2秒 1周
        _mock_now.return_value = startdatetime + timedelta(minutes=5)
        Lap_Factory(entrant=ent1)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent1.id)
        self.assertEqual(result.count(), 5)

        _mock_now.return_value = startdatetime + timedelta(minutes=4, seconds=59 )
        Lap_Factory(entrant=ent2)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)
        self.assertEqual(result.count(), 5)

        _mock_now.return_value = startdatetime + timedelta(minutes=5, seconds=1)
        Lap_Factory(entrant=ent3)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)
        self.assertEqual(result[2].id, ent3.id)
        self.assertEqual(result.count(), 5)

        _mock_now.return_value = startdatetime + timedelta(minutes=6)
        Lap_Factory(entrant=ent4)
        result = Race.objects.get_result(self.race.id)
        self.assertEqual(result[0].id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)
        self.assertEqual(result[2].id, ent3.id)
        self.assertEqual(result[3].id, ent4.id)
        self.assertEqual(result.count(), 5)

        _mock_now.return_value = startdatetime + timedelta(minutes=5, seconds=2)
        Lap_Factory(entrant=ent5)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent2.id)
        self.assertEqual(result[1].id, ent1.id)
        self.assertEqual(result[2].id, ent3.id)
        self.assertEqual(result[3].id, ent5.id)
        self.assertEqual(result[4].id, ent4.id)
        self.assertEqual(result.count(), 5)

        #ent1 5分 1周 ent2 4分59秒 1周 ent3 9分59秒 2周 ent4 6分 1周 ent5 5分2秒 1周
        _mock_now.return_value = startdatetime + timedelta(minutes=9, seconds=59)
        Lap_Factory(entrant=ent3)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent3.id)
        self.assertEqual(result[1].id, ent2.id)
        self.assertEqual(result[2].id, ent1.id)
        self.assertEqual(result[3].id, ent5.id)
        self.assertEqual(result[4].id, ent4.id)
        self.assertEqual(result.count(), 5)

        #ent1 10分 2周 ent2 4分59秒 1周 ent3 9分59秒 2周 ent4 6分 1周 ent5 5分2秒 1周
        _mock_now.return_value = startdatetime + timedelta(minutes=10)
        Lap_Factory(entrant=ent1)
        result = Race.objects.get_result(self.race.id) 
        self.assertEqual(result[0].id, ent3.id)
        self.assertEqual(result[1].id, ent1.id)
        self.assertEqual(result[2].id, ent2.id)
        self.assertEqual(result[3].id, ent5.id)
        self.assertEqual(result[4].id, ent4.id)
        self.assertEqual(result.count(), 5)

    def print_result(result):
        for item in result:
            print(f"No:{item.num} Laps:{item.lapcount} LastTime:{item.lasttime}")

class ResutInput_AddLap_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.ent2 = EntrantFactory(race=self.race)

        self.user = get_user_model().objects.first()

    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_addlap_view_true(self, _mock_now):
        startdatetime = timezone.now()
        self.client.logout()
        self.client.force_login(self.user)
        self.race.start_at = timezone.now()
        self.race.save()

        params={
            "num" : self.ent1.num
        }

        _mock_now.return_value = startdatetime + timedelta(seconds=1)
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertTrue(Lap.objects.exists())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Lap.objects.first().entrant.id, self.ent1.id)
        self.assertEqual(Lap.objects.first().created_at, datetime(2021, 1, 1, 1, 1, 2, tzinfo=timezone.utc))
        self.assertEqual(Lap.objects.first().laptime, time(0,0,1))

        _mock_now.return_value = startdatetime + timedelta(seconds=2)
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertEqual(Lap.objects.count(), 2)
        self.assertEqual(Lap.objects.all()[1].created_at, datetime(2021, 1, 1, 1, 1, 3, tzinfo=timezone.utc))
        self.assertEqual(Lap.objects.all()[1].laptime, time(0,0,1))

        _mock_now.return_value = startdatetime + timedelta(seconds=3)
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertEqual(Lap.objects.count(), 3)
        self.assertEqual(Lap.objects.all()[2].created_at, datetime(2021, 1, 1, 1, 1, 4, tzinfo=timezone.utc))
        self.assertEqual(Lap.objects.all()[2].laptime, time(0,0,1))

        _mock_now.return_value = startdatetime + timedelta(minutes=1, seconds=2)
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertEqual(Lap.objects.count(), 4)
        self.assertEqual(Lap.objects.all()[3].created_at, datetime(2021, 1, 1, 1, 2, 3, tzinfo=timezone.utc))
        self.assertEqual(Lap.objects.all()[3].laptime, time(0,0,59))

        _mock_now.return_value = startdatetime + timedelta(minutes=2, seconds=2)
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertEqual(Lap.objects.count(), 5)
        self.assertEqual(Lap.objects.all()[4].created_at, datetime(2021, 1, 1, 1, 3, 3, tzinfo=timezone.utc))
        self.assertEqual(Lap.objects.all()[4].laptime, time(0,1,00))
    
    def test_addlap_num_id(self):
        ent1 = EntrantFactory(race=self.race)
        ent2 = EntrantFactory(race=self.race)
        self.race.start_at = timezone.now()
        self.race.save()

        ent1.num = ent2.id
        ent1.save()

        ent2.num = ent1.id
        ent2.save()

        self.client.logout()
        self.client.force_login(self.user)

        params={
            "num" : ent1.num
        }

        self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertTrue(Entrant.objects.get(pk=ent1.id).lap_set.all().exists())
        self.assertFalse(Entrant.objects.get(pk=ent2.id).lap_set.all().exists())

        params={
            "num" : ent2.num
        }

        self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertEqual(Entrant.objects.get(pk=ent1.id).lap_set.all().count(), 1)
        self.assertTrue(Entrant.objects.get(pk=ent2.id).lap_set.all().exists())


    def test_addlap_view_notlogin(self):
        self.client.logout()

        params={
            "num" : self.ent1.num
        }

        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertTrue(Entrant.objects.exists())
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Lap.objects.exists())
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).lap_set.exists())
        
    def test_addlap_view_notmember(self):
        self.client.logout()
        usr2 = UserFactory()
        self.client.force_login(usr2)
        
        params={
            "num" : self.ent1.num
        }

        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertTrue(Entrant.objects.exists())
        self.assertNotEqual(response.status_code, 405)
        self.assertFalse(Lap.objects.exists())
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).lap_set.exists())

    def test_addlap_view_ngNum(self):
        self.client.logout
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num + self.ent2.num
        }

        self.assertFalse(Entrant.objects.filter(num=params["num"]).exists() )
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("input_result", kwargs={"pk":self.race.id}))

    def test_addlap_otherrace_sameNum(self):
        race2 = RaceFactory()
        EntrantFactory(race=race2, num=self.ent1.num)

        self.client.logout
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).lap_set.all().exists() )
        response = self.client.post(f"/race/{self.race.id}/inputresult/addlap", data=params)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).lap_set.all().exists() )


class GetEntrantInfo_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) :
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)

    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_getinfo(self, _mock_now):
        startdatetime = timezone.now()
        ent1 = EntrantFactory(race=self.race)
        m1 = Entrant_Member_Factory(belonging=ent1)
        m2 = Entrant_Member_Factory(belonging=ent1)
        m3 = Entrant_Member_Factory(belonging=ent1)

        _mock_now.return_value = startdatetime + timedelta(minutes=10)
        Lap_Factory(entrant=ent1)

        _mock_now.return_value = startdatetime + timedelta(minutes=20, seconds=1)
        Lap_Factory(entrant=ent1)

        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get(f"/race/entrants/{ent1.id}/getinfo")
        data = json.loads(response.content)
        self.assertEqual(data["team_name"], ent1.team_name)
        self.assertEqual(len(data["member"]), 3)
        self.assertEqual(data["member"][0], m1.name)
        self.assertEqual(data["member"][1], m2.name)
        self.assertEqual(data["member"][2], m3.name)
        
        laps = data["laps"]
        tz = pytz.timezone("Asia/Tokyo")
        self.assertEqual(len(laps.keys()), 2)
        self.assertEqual(laps["1"]["input_time"], (startdatetime + timedelta(minutes=10)).astimezone(tz).strftime("%Y/%m/%d %H:%M:%S") )
        self.assertEqual(laps["2"]["input_time"], (startdatetime + timedelta(minutes=20, seconds=1)).astimezone(tz).strftime("%Y/%m/%d %H:%M:%S"))

class deleteLap_View_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.ent2 = EntrantFactory(race=self.race)

        self.user = get_user_model().objects.first()

    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_deletelap(self, _mock_now):
        self.client.logout()
        self.client.force_login(self.user)

        startdatetime = timezone.now()
        l1 = Lap_Factory(entrant=self.ent1)

        _mock_now.return_value = startdatetime + timedelta(minutes=10)
        l2 = Lap_Factory(entrant=self.ent1)

        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 2)
        
        params={
            "num" : self.ent1.num
        }

        response = self.client.post(f"/race/{self.race.id}/inputresult/deletelap", params)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 1)
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.last().created_at, l1.created_at )
    
    @patch('django.utils.timezone.now', return_value=datetime(2021, 1, 1, 1, 1 ,1, tzinfo=timezone.utc))
    def test_deletelap_2(self, _mock_now):
        self.client.logout()
        self.client.force_login(self.user)

        startdatetime = timezone.now()
        l1 = Lap_Factory(entrant=self.ent1)

        _mock_now.return_value = startdatetime + timedelta(minutes=10)
        l2 = Lap_Factory(entrant=self.ent1)

        _mock_now.return_value = startdatetime - timedelta(minutes=10)
        l3 = Lap_Factory(entrant=self.ent1)

        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 3)
        
        params={
            "num" : self.ent1.num
        }

        response = self.client.post(f"/race/{self.race.id}/inputresult/deletelap", params)

        self.assertEqual(response.status_code, 302)

        ent = Entrant.objects.get(pk=self.ent1.id)
        self.assertEqual(ent.lap_set.count(), 2)
        self.assertTrue(ent.lap_set.filter(pk=l1.id).exists())
        self.assertFalse(ent.lap_set.filter(pk=l2.id).exists())
        self.assertTrue(ent.lap_set.filter(pk=l3.id).exists())
    
    def test_deletelap_nolap(self):
        self.client.logout()
        self.client.force_login(self.user)

        params={
            "num" : self.ent1.num
        }

        response = self.client.post(f"/race/{self.race.id}/inputresult/deletelap", params)

        self.assertEqual(response.status_code, 302)
        ent = Entrant.objects.get(pk=self.ent1.id)
        self.assertEqual(ent.lap_set.count(), 0)

    def test_deletelap_notmember(self):
        self.client.logout()
        usr2 = UserFactory()
        self.client.force_login(usr2)

        Lap_Factory(entrant=self.ent1)
        
        params={
            "ent_id" : self.ent1.num
        }
        
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 1)
        response=self.client.post(f"/race/{self.race.id}/inputresult/deletelap", params)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 1)


    def test_deletelap_notlogin(self):
        self.client.logout()

        Lap_Factory(entrant=self.ent1)
        
        params={
            "ent_id" : self.ent1.num
        }
        
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 1)
        response=self.client.post(f"/race/{self.race.id}/inputresult/deletelap", params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).lap_set.count(), 1)

    def test_deletelap_num_id(self):
        ent1 = EntrantFactory(race=self.race)
        ent2 = EntrantFactory(race=self.race)

        ent1.num = ent2.id
        ent1.save()
        Lap_Factory(entrant=ent1)

        ent2.num = ent1.id
        ent2.save()
        Lap_Factory(entrant=ent2)

        self.client.logout()
        self.client.force_login(self.user)

        params={
            "num" : ent1.num
        }

        self.client.post(f"/race/{self.race.id}/inputresult/deletelap", data=params)
        self.assertFalse(Entrant.objects.get(pk=ent1.id).lap_set.all().exists())
        self.assertTrue(Entrant.objects.get(pk=ent2.id).lap_set.all().exists())

        params={
            "num" : ent2.num
        }

        self.client.post(f"/race/{self.race.id}/inputresult/deletelap", data=params)
        self.assertFalse(Entrant.objects.get(pk=ent1.id).lap_set.all().exists())
        self.assertFalse(Entrant.objects.get(pk=ent2.id).lap_set.all().exists())

    def test_deletelap_view_ngNum(self):
        self.client.logout
        self.client.force_login(self.user)

        Lap_Factory(entrant=self.ent1)

        params = {
            "num" : self.ent1.num + self.ent2.num
        }

        self.assertFalse(Entrant.objects.filter(num=params["num"]).exists() )
        response = self.client.post(f"/race/{self.race.id}/inputresult/deletelap", data=params)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("input_result", kwargs={"pk":self.race.id}))

    def test_deletelap_otherrace_sameNum(self):
        race2 = RaceFactory()
        o_ent1 = EntrantFactory(race=race2, num=self.ent1.num)
        Lap_Factory(entrant=self.ent1)
        Lap_Factory(entrant=o_ent1)

        self.client.logout
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).lap_set.all().exists() )
        response = self.client.post(f"/race/{self.race.id}/inputresult/deletelap", data=params)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).lap_set.all().exists() )

class RaceShowResult_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)

    def test_access(self):
        self.client.logout()
        valids = [RaceStatus.RACE_STATUS_HOLD, RaceStatus.RACE_STATUS_END]
        invalids = [RaceStatus.RACE_STATUS_DEFAULT, RaceStatus.RACE_STATUS_ENTRY, RaceStatus.RACE_STATUS_CANCEL]

        for valid in valids:
            with self.subTest(valid=valid):
                self.race.status = RaceStatus.objects.get(pk=valid)
                self.race.save()
                response = self.client.get(reverse("show_result", kwargs={"pk": self.race.id}))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'race/race_result.html')
        
        for invalid in invalids:
            with self.subTest(invalid=invalid):
                self.race.status = RaceStatus.objects.get(pk=invalid)
                self.race.save()
                response = self.client.get(reverse("show_result", kwargs={"pk": self.race.id}))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'race/result_notshow.html')

class SetDNF_View_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.ent2 = EntrantFactory(race=self.race)

    def test_setDNF_view_access_get(self):
        self.client.logout()
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        response = self.client.get(reverse('race_setdnf', kwargs={"pk":self.race.id}), params)
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_post(self):
        self.client.logout()
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        response = self.client.post(reverse('race_setdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_notlogin(self):
        self.client.logout()

        params = {
            "num" : self.ent1.num
        }

        response = self.client.post(reverse('race_setdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        params = {
            "num" : self.ent1.num
        }

        response = self.client.post(reverse('race_setdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf)
    
    def test_setDNF_otherrace_sameNum(self):
        race2 = RaceFactory()
        o_ent1 = EntrantFactory(race=race2, num=self.ent1.num)

        self.client.logout
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf )
        response = self.client.post(reverse('race_setdnf', kwargs={"pk":self.race.id}), params)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        self.assertFalse(Entrant.objects.get(pk=o_ent1.id).is_dnf )

class UnSetDNF_View_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.ent2 = EntrantFactory(race=self.race)

    def test_unsetDNF_view_access_get(self):
        self.client.logout()
        self.client.force_login(self.user)
        self.ent1.is_dnf = True
        self.ent1.save()

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        response = self.client.get(reverse('race_unsetdnf', kwargs={"pk":self.race.id}), params)
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_post(self):
        self.client.logout()
        self.client.force_login(self.user)
        self.ent1.is_dnf = True
        self.ent1.save()

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        response = self.client.post(reverse('race_unsetdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_notlogin(self):
        self.client.logout()
        self.ent1.is_dnf = True
        self.ent1.save()

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        response = self.client.post(reverse('race_unsetdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_setDNF_view_access_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())
        self.ent1.is_dnf = True
        self.ent1.save()

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        response = self.client.post(reverse('race_unsetdnf', kwargs={"pk":self.race.id}), params)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf)

    def test_unsetDNF_otherrace_sameNum(self):
        self.ent1.is_dnf = True
        self.ent1.save()

        race2 = RaceFactory()
        o_ent1 = EntrantFactory(race=race2, num=self.ent1.num)
        o_ent1.is_dnf = True
        o_ent1.save()

        self.client.logout
        self.client.force_login(self.user)

        params = {
            "num" : self.ent1.num
        }

        self.assertTrue(Entrant.objects.get(pk=self.ent1.id).is_dnf )
        response = self.client.post(reverse('race_unsetdnf', kwargs={"pk":self.race.id}), params)
        self.assertFalse(Entrant.objects.get(pk=self.ent1.id).is_dnf)
        self.assertTrue(Entrant.objects.get(pk=o_ent1.id).is_dnf )
