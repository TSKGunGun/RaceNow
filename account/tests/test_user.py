from django import test
from django.core.exceptions import ValidationError
from django.http import response
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

class UserProfile_Detail_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
        self.client.logout()
        self.client.force_login(self.user)
    
    def test_getresponse_detail(self):
        response = self.client.get(f'/account/{self.user.pk}/detail')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertTemplateUsed('account/user_detail.html')

    def test_getresponse_notfound(self):
        response = self.client.get('/account/2/detail')

        self.assertEqual(response.status_code, 404)
        #self.assertTemplateUsed('account/user_detail_notfound.html')

class User_Organizers_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
        self.org = Organizer.objects.create(
            owner = self.user,
            name="org1",
            email_address = "test@example.com"
        )

    def test_get_user_orginers(self):
        self.org.members.add(self.user)

        self.assertEqual(self.org.members.count(), 1)

        orgs = self.user.organizers.all()
        self.assertEqual(orgs.count(), 1)
        self.assertEqual(orgs.first().name, "org1")

        org2 = Organizer.objects.create(
            owner = self.user,
            name="org2",
            email_address = "test@example.com"
        )
        org2.members.add(self.user)
        orgs = self.user.organizers.all()
        self.assertEqual(orgs.count(), 2)
        self.assertEqual(orgs.last().name, "org2")

class Account_Detail_Test(TestCase):
    def setUp(self) -> None:
        self.testuser1 = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )

        self.testuser2 = get_user_model().objects.create_user(
            username="testuser2",
            password="password"
        )

        self.org = Organizer.objects.create(
            owner = self.testuser1,
            name="org1",
            email_address = "test@example.com"
        )
        self.org.members.add(self.testuser1, self.testuser2)

    def test_delete_organizer(self):
        self.client.logout()
        self.client.force_login(self.testuser1)
        self.assertEqual(self.org.members.count(), 2)
        
        with self.assertRaises(ValidationError):
            self.client.post( '/account/deleteOrgMember', data={'organizer': self.org.id})        

        self.client.logout()
        self.client.force_login(self.testuser2)
        
        response = self.client.post( '/account/deleteOrgMember', data={'organizer': self.org.id})
        self.assertEqual(self.org.members.count(), 1)
        self.assertRedirects(response, f"/account/{self.testuser2.pk}/detail")
        
    def test_add_organizer_notlogin(self):
        org2 = Organizer.objects.create(
            owner = self.testuser1,
            name="org2",
            email_address = "test@example.com"
        )
        org2.members.add(self.testuser1)
        
        self.client.logout()
        self.client.force_login(self.testuser2)
        response = self.client.post( '/account/addOrgMember',{'organizer':org2.id})
        self.assertEqual(org2.members.count(), 2)
        self.assertRedirects(response, f"/account/{self.testuser2.pk}/detail")

        response = self.client.post( '/account/addOrgMember', {'organizer':org2.id})
        self.assertEqual(org2.members.count(), 2)
        self.assertRedirects(response, f"/account/{self.testuser2.pk}/detail")          
        
        self.client.logout()
        self.client.force_login(self.testuser1)
        response = self.client.post( '/account/addOrgMember', {'organizer':org2.id})
        self.assertEqual(org2.members.count(), 2)
        self.assertRedirects(response, f"/account/{self.testuser1.pk}/detail")          