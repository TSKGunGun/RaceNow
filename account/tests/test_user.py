from django import test
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer, User, CustomUsernameValidator
from account.forms import CustomUserCreationForm
from account.views import CreateUserView

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
    
    def test_username_validator(self):
        valid_usernames = ["test", "test_test", "test123456789", "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        invalid_usernames = ["あああ", "test-test", "αα", "亜亜"]
        validator = CustomUsernameValidator()

        for valid in valid_usernames:
            with self.subTest(valid=valid):
                validator(valid)
        
        for invalid in invalid_usernames:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValidationError):
                    validator(invalid)

class LoginView_Test(TestCase):
    def test_request_login(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

class CreateUserView_Test(TestCase):
    def test_view_response(self):
        response = self.client.get('/account/create')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/create_user.html")

    def test_view_create(self):
        params = {
            "username": "test_user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        self.assertEqual(get_user_model().objects.count(), 0)
        response = self.client.post("/account/create", data=params)

        self.assertEqual(get_user_model().objects.count(), 1)
        
        createuser = get_user_model().objects.first()
        self.assertEqual(createuser.username, params["username"])
        self.assertRedirects(response, "/")
    
    def test_unique_username(self):
        params = {
            "username": "test_user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        params2 = {
            "username": "test_user2",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        self.assertEqual(get_user_model().objects.count(), 0)
        response = self.client.post("/account/create", data=params)

        self.assertEqual(get_user_model().objects.count(), 1)

        response = self.client.post("/account/create", data=params)
        self.assertEqual(get_user_model().objects.count(), 1)

        response = self.client.post("/account/create", data=params2)
        self.assertEqual(get_user_model().objects.count(), 2)


class CreateUserForm_Test(TestCase):
    def test_form_create(self):
        params = {
            "username": "test_user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        user = User()
        form = CustomUserCreationForm(params, instance=user)
        form.is_valid()

        self.assertEqual(get_user_model().objects.count(), 0)
        form.save()

        self.assertEqual(get_user_model().objects.count(), 1)
        
        createuser = get_user_model().objects.first()
        self.assertEqual(createuser.username, params["username"])
    
    def test_form_validate(self):
        valid_params = {
            "username": "test_user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }
        
        invalid_params = {
            "username": "test-user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        user = User()
        form = CustomUserCreationForm(valid_params, instance=user)
        form.is_valid()
        self.assertEquals(len(form.errors), 0)

        form = CustomUserCreationForm(invalid_params, instance=user)
        form.is_valid()
        self.assertEquals(len(form.errors), 1)
        self.assertTrue(  "ユーザ名は英数字,もしくはアンダーバー(_)のみが使用できます。" in form.errors.as_text() )

    def test_unique_username(self):
        params = {
            "username": "test_user",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        params2 = {
            "username": "test_user2",
            "password1": "J0WOe9eH",
            "password2": "J0WOe9eH"
        }

        user = User()
        form = CustomUserCreationForm(params, instance=user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(get_user_model().objects.count(), 1)

        form2 = CustomUserCreationForm(params, instance=user)
        self.assertTrue(form2.is_valid())
        form2.save()
        self.assertEqual(get_user_model().objects.count(), 1)