from time import timezone
from django.test import TestCase
from race.models import Race
from .factories import RaceFactory, EntrantFactory, Entrant_Member_Factory, Lap_Factory
from datetime import datetime, timedelta
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