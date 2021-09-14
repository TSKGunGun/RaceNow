from django import test
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Organizer, User, CustomUsernameValidator
from .forms import CustomUserCreationForm
from .views import CreateUserView

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

class Username_Validation_Test(TestCase):
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


class Organizer_Model_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )

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
