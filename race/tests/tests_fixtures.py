from django.test import TestCase
from race.models import Race, RaceStatus, Category, RaceType

# Create your tests here.
class Custom_TestCase(TestCase):
  fixtures = ['race_default.json']

class CategoryTest(Custom_TestCase):
    def test_defaultItems(self):
        
        self.assertEqual(Category.objects.get(pk=1).name, "オンロードレース")
        self.assertEqual(Category.objects.get(pk=2).name, "オフロードレース")

class RaceTypeTest(Custom_TestCase):
    def test_defalutItems(self):
        racetype = RaceType.objects.all()

        self.assertEqual(racetype.get(pk=1).name, "サーキット")
        self.assertEqual(racetype.get(pk=2).name, "モトクロス")
        self.assertEqual(racetype.get(pk=3).name, "クロスカントリー")

class RaceStatusTest(Custom_TestCase):
    def test_defaultItems(self):
        self.assertEqual(RaceStatus.objects.get(pk=1).name, "レース開催前")
        self.assertEqual(RaceStatus.objects.get(pk=2).name, "レース開催中")
        self.assertEqual(RaceStatus.objects.get(pk=3).name, "レース終了")
        self.assertEqual(RaceStatus.objects.get(pk=4).name, "レース中止")