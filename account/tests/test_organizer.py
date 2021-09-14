from django import test
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer, User

class Organizer_Model_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
        
    def test_create_organizer(self):
        name = "test_org"
        org = Organizer.objects.create(
            owner = self.user,
            name=name,
            email_address = "test@example.com"
        )

        org.save()
        create_org = Organizer.objects.first()
        self.assertEqual(org.name, name)

    def test_is_organizer_member(self):
        test_organizer = Organizer.objects.create(
            owner = self.user,
            name = "test_organizer",
            email_address = "test@example.com",
            url = "test@example.com"
        )

        self.assertEqual(0, len(test_organizer.members.all()))
        
        test_organizer.members.add(self.user)
        self.assertEqual(1, len(test_organizer.members.all()))
        self.assertEqual(test_organizer.members.all().first(), self.user)