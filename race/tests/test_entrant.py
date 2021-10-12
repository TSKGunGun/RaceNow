from django.core.exceptions import ValidationError
from django.test import TestCase
from race.models import NumValidator, Race
from race.forms import AddEntrantForm
from .factories import EntrantFactory, RaceFactory
from account.tests.factories import UserFactory, OrganizerFactory
from django.urls import reverse
import json

class AddEntrantForm_Input_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        
    def test_input_all(self):
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = AddEntrantForm(race=self.race, data=params)
        self.assertTrue(form.is_valid())

    def test_no_input_teamname(self):
        params = {
            "team_name" : "",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = AddEntrantForm(race=self.race, data=params)
        self.assertTrue(form.is_valid())

    def test_no_input_Num(self):
        params = {
            "team_name" : "",
            "num" :  "",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = AddEntrantForm(race=self.race, data=params )
        self.assertFalse(form.is_valid())
        self.assertIn('num', form.errors)

    def test_no_input_member(self):
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : ""
        }

        form = AddEntrantForm(race=self.race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn('members', form.errors)
        self.assertEqual(form.errors["members"], ["メンバーが1名も追加されていません。"])

    def test_input_member_over_max(self):
        race = RaceFactory(organizer=self.org, team_member_count_max=1)

        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" :  json.dumps( { "0" : { "name" : "test1"}, "1" : { "name" : "test2"} })
        }

        form = AddEntrantForm(race=race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn('members', form.errors)
        self.assertEqual(form.errors["members"], ["メンバーが最大人数を超えています。"])
    
    def test_input_member_under_min(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=2, team_member_count_max=2)

        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" :  json.dumps( { "0" : { "name" : "test"}})
        }

        form = AddEntrantForm(race=race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn('members', form.errors)
        self.assertEqual(form.errors["members"], ["メンバーが最少人数を満たしていません。"])

    def test_input_notNum(self):
        params = {
            "team_name" : "Test",
            "num" :  "55a",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = AddEntrantForm(race=self.race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn("num", form.errors)

    def test_post_samenum(self):
        ent1 = EntrantFactory(race = self.race)

        params = {
            "team_name" : "Test",
            "num" :  ent1.num,
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }
    
        form = AddEntrantForm(race=self.race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn('num', form.errors)
        self.assertEqual(form.errors["num"], [f"入力したゼッケンNo: {params['num']} は既に使用されています。"])

class Entrant_Num_Validation_Test(TestCase):
    def atest_validation(self):
        valids = ["12", "0123", "123456789"]
        invalids = ["123あ", "123１", "123l", "abc", "あいうえお"]
        validator = NumValidator()

        for valid in valids:
            with self.subTest(valid=valid):
                validator(valid)

        for invalid in invalids:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    validator(invalid)

class View_AddEntrant_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)

    def test_get_AddEntrantPage(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('add_entrant', kwargs={"pk":self.race.id}))

        self.assertEqual(response.status_code, 200)

    def test_getAddEntrantPage_NotLogin(self):
        self.client.logout()
        
        response = self.client.get(reverse('add_entrant', kwargs={"pk":self.race.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_getAddEntrantPage_NotMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        response = self.client.get(reverse('add_entrant', kwargs={"pk":self.race.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_post_AddEntrantPage(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        self.assertFalse(Race.objects.get(pk=self.race.id).entrant_set.all().exists())
        response = self.client.post(reverse('add_entrant', kwargs={"pk":self.race.id}), params)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Race.objects.get(pk=self.race.id).entrant_set.all().exists())

    
    def test_post_AddEntrantPage_notlogin(self):
        self.client.logout()
        
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        self.assertFalse(Race.objects.get(pk=self.race.id).entrant_set.all().exists())
        response = self.client.post(reverse('add_entrant', kwargs={"pk":self.race.id}), params)

        self.assertFalse(Race.objects.get(pk=self.race.id).entrant_set.all().exists())

    def test_post_AddEntrantPage_notMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())
        
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        self.assertFalse(Race.objects.get(pk=self.race.id).entrant_set.all().exists())
        response = self.client.post(reverse('add_entrant', kwargs={"pk":self.race.id}), params)

        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(Race.objects.get(pk=self.race.id).entrant_set.all().exists())

class Test_entrants_ListView(TestCase):    
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.ent2 = EntrantFactory(race=self.race)
    
    def test_entrant_View(self):
        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get(reverse('entrant_index', kwargs={'pk':self.race.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('race/entrant_list.html')
        self.assertContains(response, text=self.ent1.team_name)
        self.assertContains(response, text=self.ent2.team_name)
    
    def test_entrant_View_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        response = self.client.get(reverse('entrant_index', kwargs={'pk':self.race.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('race/entrant_list.html')
        self.assertContains(response, text=self.ent1.team_name)
        self.assertContains(response, text=self.ent2.team_name)

    def test_entrant_view_notlogin(self):
        self.client.logout()

        response = self.client.get(reverse('entrant_index', kwargs={'pk':self.race.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('race/entrant_list.html')
        self.assertContains(response, text=self.ent1.team_name)
        self.assertContains(response, text=self.ent2.team_name)