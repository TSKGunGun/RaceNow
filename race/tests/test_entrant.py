from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from race.models import Entrant, NumValidator, Race
from race.forms import EditEntrantForm, EntrantCSVUploadForm
from racenow.settings import BASE_DIR
from .factories import Entrant_Member_Factory, EntrantFactory, RaceFactory
from account.tests.factories import UserFactory, OrganizerFactory
from django.urls import reverse
import json, os

class EditEntrantForm_Input_Test(TestCase):
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

        form = EditEntrantForm(race=self.race, data=params)
        self.assertTrue(form.is_valid())

    def test_no_input_teamname(self):
        params = {
            "team_name" : "",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = EditEntrantForm(race=self.race, data=params)
        self.assertTrue(form.is_valid())

    def test_no_input_Num(self):
        params = {
            "team_name" : "",
            "num" :  "",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = EditEntrantForm(race=self.race, data=params )
        self.assertFalse(form.is_valid())
        self.assertIn('num', form.errors)

    def test_no_input_member(self):
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : ""
        }

        form = EditEntrantForm(race=self.race, data=params)
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

        form = EditEntrantForm(race=race, data=params)
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

        form = EditEntrantForm(race=race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn('members', form.errors)
        self.assertEqual(form.errors["members"], ["メンバーが最少人数を満たしていません。"])

    def test_input_notNum(self):
        params = {
            "team_name" : "Test",
            "num" :  "55a",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        form = EditEntrantForm(race=self.race, data=params)
        self.assertFalse(form.is_valid())
        self.assertIn("num", form.errors)

    def test_post_samenum(self):
        ent1 = EntrantFactory(race = self.race)

        params = {
            "team_name" : "Test",
            "num" :  ent1.num,
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }
    
        form = EditEntrantForm(race=self.race, data=params)
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

class Test_ImportEntrantCSVData(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)

    def test_loadcsv(self):
        self.client.logout()
        self.client.force_login(self.user)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.entrant_set.all().count(), 1)
        ent = race.entrant_set.all()[0]
        self.assertEqual(ent.num, '1')
        self.assertEqual(ent.team_name, "Team_Test1")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider1-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider1-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider1-3")

    def test_loadcsv_multiple(self):
        self.client.logout()
        self.client.force_login(self.user)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_multiple.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.entrant_set.all().count(), 3)
        
        ent = race.entrant_set.all()[0]
        self.assertEqual(ent.num, '1')
        self.assertEqual(ent.team_name, "Team_Test1")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider1-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider1-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider1-3")

        ent = race.entrant_set.all()[1]
        self.assertEqual(ent.num, '2')
        self.assertEqual(ent.team_name, "Team_Test2")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider2-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider2-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider2-3")

        ent = race.entrant_set.all()[2]
        self.assertEqual(ent.num, '3')
        self.assertEqual(ent.team_name, "Team_Test3")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider3-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider3-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider3-3")

    def test_loadcsv_update(self):
        self.client.logout()
        self.client.force_login(self.user)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_multiple.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.entrant_set.all().count(), 3)

        filepath2 = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_update.csv')
        with open(filepath2) as f2:
            dummyFile2 = SimpleUploadedFile(name=f2.name, content=bytes(f2.read(), encoding=f2.encoding))
            params2 = {
                "file" : dummyFile2
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params2)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.entrant_set.all().count(), 3)
        
        ent = race.entrant_set.all()[0]
        self.assertEqual(ent.num, '1')
        self.assertEqual(ent.team_name, "Team_Test1")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider1-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider1-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider1-3")

        ent = race.entrant_set.all()[1]
        self.assertEqual(ent.num, '2')
        self.assertEqual(ent.team_name, "Team_TestU2")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider2-1U")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider2-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider2-3")

        ent = race.entrant_set.all()[2]
        self.assertEqual(ent.num, '3')
        self.assertEqual(ent.team_name, "Team_Test3")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider3-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider3-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider3-3")

    def test_loadcsv_samenum(self):
        self.client.logout()
        self.client.force_login(self.user)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_samenum.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertEqual(race.entrant_set.all().count(), 2)
        
        ent = race.entrant_set.all()[0]
        self.assertEqual(ent.num, '1')
        self.assertEqual(ent.team_name, "Team_Test3")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider3-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider3-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider3-3")

        ent = race.entrant_set.all()[1]
        self.assertEqual(ent.num, '2')
        self.assertEqual(ent.team_name, "Team_Test2")
        self.assertEqual(ent.entrant_member_set.all().count(), 3)
        self.assertEqual(ent.entrant_member_set.all()[0].name, "Test_Rider2-1")
        self.assertEqual(ent.entrant_member_set.all()[1].name, "Test_Rider2-2")
        self.assertEqual(ent.entrant_member_set.all()[2].name, "Test_Rider2-3")

    def test_loadcsv_notlogin(self):
        self.client.logout()
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        response = self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertFalse(race.entrant_set.all().exists())
    
    def test_loadcsv_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        response = self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertFalse(race.entrant_set.all().exists())
        self.assertEqual(response.status_code, 403)
    
    def test_loadcsv_ErrorData(self):
        self.client.logout()
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_NotInputMember.csv')

        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }

        self.client.post(reverse('entrant_uploadCSV', kwargs={"pk":self.race.id}), params)           
        
        race = Race.objects.get(pk=self.race.id)
        self.assertFalse(race.entrant_set.all().exists())

class Test_EntrantCSVUploadForm(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
    
    def test_valid_true(self):
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=self.race, data=params, files=params)
        self.assertTrue(form.is_valid())

        data = form.cleaned_data["file"]
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]), 3)
        self.assertEqual(data[0][0], '1')
        self.assertEqual(data[0][1], 'Team_Test1')
        self.assertEqual(data[0][2], 'Test_Rider1-1,Test_Rider1-2,Test_Rider1-3')
    
    def test_over_member(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=2)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("メンバー数がチーム最大人数を超過しています。", form.errors["file"])

    def test_under_member(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=4, team_member_count_max=5)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("メンバー数がチーム最小人数を下回っています。", form.errors["file"])

    def test_num_notdecimal(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_numnotdecimal.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("CSVファイルにゼッケンNoが数字ではない行があります。", form.errors["file"])

    def test_num_empty(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_numempty.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("CSVファイルにゼッケンNoが空の行があります。", form.errors["file"])

    def test_none_member(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_NotInputMember.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("CSVファイルにメンバーが１人もない行があります。", form.errors["file"])
    
    def test_notcsv(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("CSVファイルではありません。", form.errors["file"])

    def test_unmatchformat(self):
        race = RaceFactory(organizer=self.org, team_member_count_min=1, team_member_count_max=3)
        filepath = os.path.join(BASE_DIR, 'race/tests/files/test_entrant/test_loadcsv_unmatchformat.csv')
        
        with open(filepath) as f:
            dummyFile = SimpleUploadedFile(name=f.name, content=bytes(f.read(), encoding=f.encoding))
            params = {
                "file" : dummyFile
            }
        
        form = EntrantCSVUploadForm(race=race, data=params, files=params)
        self.assertFalse(form.is_valid())
        self.assertIn("CSVファイルのフォーマットが異なります。(列が３列では有りません。)", form.errors["file"])

class View_EditEntrant_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.em1 = Entrant_Member_Factory(belonging=self.ent1)

    def test_get_EditEntrantPage(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))

        self.assertEqual(response.status_code, 200)

    def test_getAddEntrantPage_NotLogin(self):
        self.client.logout()
        
        response = self.client.get(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_getAddEntrantPage_NotMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        response = self.client.get(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))

        self.assertNotEqual(response.status_code, 200)

    def test_post_EditEntrantPage(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        member_name = "test_edit_01"

        params = {
            "team_name" : self.ent1.team_name + "_edit",
            "num" :  self.ent1.num + "99",
            "members" : json.dumps( { "0" : { "name" : member_name}})
        }
        self.assertNotEqual(self.ent1.entrant_member_set.all()[0].name, member_name)

        response = self.client.post(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}), params)
        self.assertEqual(Race.objects.get(pk=self.race.id).entrant_set.all().count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Race.objects.get(pk=self.race.id).entrant_set.all().count(), 1)

        ent = Entrant.objects.get(pk=self.ent1.id)
        self.assertEqual(ent.team_name, self.ent1.team_name+"_edit")
        self.assertEqual(ent.num, self.ent1.num+"99")
        self.assertEqual(ent.entrant_member_set.all()[0].name, member_name)
    
    def test_post_AddEntrantPage_notlogin(self):
        self.client.logout()
        
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).team_name, self.ent1.team_name )
        response = self.client.post(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}), params)

        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).team_name, self.ent1.team_name )

    def test_post_AddEntrantPage_notMember(self):
        self.client.logout()
        self.client.force_login(UserFactory())
        
        params = {
            "team_name" : "Test",
            "num" :  "55",
            "members" : json.dumps( { "0" : { "name" : "test"}})
        }

        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).team_name, self.ent1.team_name )
        response = self.client.post(reverse('edit_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}), params)

        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(Entrant.objects.get(pk=self.ent1.id).team_name, self.ent1.team_name )


class View_DeleteEntrant_Test(TestCase):
    fixtures = ['race_default.json']

    def setUp(self) -> None:
        self.user = UserFactory()
        self.org = OrganizerFactory(members=(self.user,))
        self.race = RaceFactory(organizer=self.org)
        self.ent1 = EntrantFactory(race=self.race)
        self.em1 = Entrant_Member_Factory(belonging=self.ent1)

        self.ent2 = EntrantFactory(race=self.race)
        self.em2 = Entrant_Member_Factory(belonging=self.ent2)
    
    def test_access_get(self):
        self.client.logout()
        self.client.force_login(self.user)

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.get(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertNotEqual(self.race.entrant_set.all().count(), 1)
        self.assertNotEqual(response.status_code, 302)

    def test_access_get_notlogin(self):
        self.client.logout()

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.get(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertNotEqual(self.race.entrant_set.all().count(), 1)
        self.assertNotEqual(response.status_code, 302)

    def test_access_get_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.get(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertNotEqual(self.race.entrant_set.all().count(), 1)
        self.assertEqual(response.status_code, 405)

    def test_post_delete(self):
        self.client.logout()
        self.client.force_login(self.user)

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.post(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertEqual(self.race.entrant_set.all().count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_access_post_notlogin(self):
        self.client.logout()

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.get(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertNotEqual(self.race.entrant_set.all().count(), 1)
        self.assertNotEqual(response.status_code, 302)

    def test_access_post_notmember(self):
        self.client.logout()
        self.client.force_login(UserFactory())

        self.assertEqual(self.race.entrant_set.all().count(), 2)
        response = self.client.post(reverse('delete_entrant', kwargs={"pk":self.race.id, "ent_pk":self.ent1.id}))
        
        self.assertNotEqual(self.race.entrant_set.all().count(), 1)
        self.assertEqual(response.status_code, 403)
    