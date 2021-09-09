from racenow.settings import AUTH_USER_MODEL
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User

# Create your tests here.
class UserModelTest(TestCase):
    def test_getcustomuser_getusermodel(self):
        custom_user_model = User
        self.assertEqual(custom_user_model, get_user_model())

    def test_getcustomuser_auth_user(self):
        custom_user_model = User()
        self.assertEqual(custom_user_model, AUTH_USER_MODEL)