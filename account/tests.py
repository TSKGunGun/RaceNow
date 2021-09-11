from operator import truediv

from django.http import response
from racenow.settings import AUTH_USER_MODEL
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Organizer

# Create your tests here.
class UserModel_Create_Test(TestCase):
    def test_normaluser_create(self):
        username = "test"
        user=get_user_model().objects.create_user(
            username=username, 
            password="password")
        user.save()

        createuser = get_user_model().objects.all().first()

        self.assertEqual(createuser.username, username)
        self.assertEqual(createuser.is_staff, False)
    
    def test_staffuser_create(self):
        username = "test"
        user=get_user_model().objects.create_user(
            username=username, 
            password="password", is_staff=True)
        user.save()

        createuser = get_user_model().objects.all().first()

        self.assertEqual(createuser.username, username)
        self.assertEqual(createuser.is_staff, True)

class Organizer_Create_Test(TestCase):
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

class LoginView_Test(TestCase):
    def test_request_login(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

class LogoutView_Test(TestCase):
    def test_request_logout(self):
        response = self.client.get('/logout/')

        self.assertEqual(response.status_code, 200)