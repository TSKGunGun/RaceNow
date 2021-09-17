from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Place
from .forms import CreatePlaceForm


# Create your tests here.
class Place_Model_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username = "test_user",
            password = "password"
        )

    def test_create_place(self):
        self.assertEqual(Place.objects.count(), 0)

        place = Place.objects.create(
            owner = self.user,
            name = "test_place",
            address = "test_address",
            url = "test.example.com"
        )

        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(Place.objects.first(), place)

class Place_CreateForm_Test(TestCase):
    def test_invalid_notinput(self):
        params = {
            "name" : "",
            "address" : "test_address",
        }

        place = Place()
        form = CreatePlaceForm(params, instance=place)
        self.assertFalse(form.is_valid())

        params = {
            "name" : "test_place",
            "address" : "",
        }

        place = Place()
        form = CreatePlaceForm(params, instance=place)
        self.assertFalse(form.is_valid())

        
        params = {
            "name" : "test_place",
            "address" : "test_address",
            "url":"testexamplecom"
        }

        place = Place()
        form = CreatePlaceForm(params, instance=place)
        self.assertFalse(form.is_valid())

    def test_valid_input(self):
        params = {
            "name" : "test_place",
            "address" : "test_address"
        }

        place = Place()
        form = CreatePlaceForm(params, instance=place)
        self.assertTrue(form.is_valid())

        params = {
            "name" : "test_place",
            "address" : "test_address",
            "url" : "test.example.com"
        }

        place = Place()
        form = CreatePlaceForm(params, instance=place)
        self.assertTrue(form.is_valid())
    
class Place_CreateView_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username = "test_user",
            password = "password"
        )
    
    def test_view_access_notlogin(self):
        self.client.logout()

        response = self.client.get("/place/create")
        self.assertEqual(response.status_code, 302)
    
    def test_view_access_logined(self):
        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get("/place/create")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "place/create.html")

    def test_view_create(self):
        self.client.logout()
        self.client.force_login(self.user)

        params ={
            "name":"test_place",
            "address":"test_address",
            "url":""
        }
    
        self.assertEqual(Place.objects.count(), 0)
        response = self.client.post("/place/create", params)
        
        self.assertEqual(Place.objects.count(), 1)
        self.assertRedirects(response, f'/place/{Place.objects.first().id}/detail')


class Place_DetailView_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username = "test_user",
            password = "password"
        )
        self.place = Place.objects.create(
            owner = self.user,
            name = "test_place",
            address = "test_place_address"
        )
    
    def test_view_access_notlogin(self):
        self.client.logout()

        response = self.client.get(f"/place/{self.place.pk}/detail")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "place/detail.html")
    
    def test_view_access_logined(self):
        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get(f"/place/{self.place.pk}/detail")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "place/detail.html")

    def test_detail_content(self):
        response = self.client.get(f"/place/{self.place.pk}/detail")

        self.assertContains(response, "test_place")