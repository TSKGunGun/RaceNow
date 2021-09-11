from operator import truediv
from racenow.settings import AUTH_USER_MODEL
from django.test import TestCase
from django.contrib.auth import get_user_model

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