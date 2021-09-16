from django import test
from django.http import response
from django.test import TestCase
from django.contrib.auth import get_user_model
from account.models import Organizer, User
from account.forms import CreateOrganizerForm

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

class CreateOrganizer_Form_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
    
    def test_validation_True(self):
        params = {
            "name" : "test_org",
            "email_address" : "test@example.com",
            "url":"test@example.com"
        }
        
        org = Organizer()
        form = CreateOrganizerForm(params, instance=org)
        
        self.assertTrue(form.is_valid())

    def test_validation_email(self):
        params = {
            "name" : "test_org",
            "email_address" : "test_example.com",
            "url":"test@example.com"
        }

        org = Organizer()
        form = CreateOrganizerForm(params, instance=org)
        self.assertFalse(form.is_valid())

        params["email_address"] = "test@example@example.com"
        form = CreateOrganizerForm(params, instance=org)
        self.assertFalse(form.is_valid())

        params["email_address"] = "test@example.com"
        form = CreateOrganizerForm(params, instance=org)
        self.assertTrue(form.is_valid())

    def test_validation_url(self):
        params = {
            "name" : "test_org",
            "email_address" : "test@example.com",
            "url":"test_example,com"
        }

        org = Organizer()
        form = CreateOrganizerForm(params, instance=org)
        self.assertFalse(form.is_valid())

        params["url"] = "test_examplecom"
        form = CreateOrganizerForm(params, instance=org)
        self.assertFalse(form.is_valid())

        params["url"] = "test_example.com"
        form = CreateOrganizerForm(params, instance=org)
        self.assertFalse(form.is_valid())


class CreateOrganizer_View_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
    
    def test_view_access(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get('/organizer/create')
        self.assertEqual(response.status_code, 200)
    
    def test_view_template(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get('/organizer/create')
        self.assertTemplateUsed(response, "organizer/create.html")
    
    def test_create_organizer(self):
        self.assertEqual(Organizer.objects.count(), 0)
        
        self.client.logout()
        self.client.force_login(self.user)

        params = {
            "name" : "test_organizer",
            "email_address" : "test@example.com",
            "url" : "text.example.com"
        }
        response = self.client.post("/organizer/create", data=params)
        self.assertEqual(Organizer.objects.count(), 1)

        org = Organizer.objects.first()
        self.assertRedirects(response, f'/organizer/{org.id}/detail')

    def test_create_invalid_organizer(self):
        self.assertEqual(Organizer.objects.count(), 0)
        
        self.client.logout()
        self.client.force_login(self.user)

        params = {
            "name" : "test_organizer",
            "email_address" : "test-example.com",
            "url" : "text.example.com"
        }
        response = self.client.post("/organizer/create", data=params)
        self.assertEqual(Organizer.objects.count(), 0)
        

class OrganizerDetail_View_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="password"
        )
        self.org = Organizer.objects.create(
            owner = self.user,
            name = "test_organizer",
            email_address = "test@example.com",
            url = "text.example.com"
        )
    
    def test_view_access_notlogin(self):
        self.client.logout()
        
        response = self.client.get(f'/organizer/{self.org.pk}/detail')
        self.assertEqual(response.status_code, 200)

    def test_view_access_notlogin(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f'/organizer/{self.org.pk}/detail')
        self.assertEqual(response.status_code, 200)
    
    def test_view_template(self):
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(f'/organizer/{self.org.pk}/detail')
        self.assertTemplateUsed(response, "organizer/detail.html")
