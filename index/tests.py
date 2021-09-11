from django.http import response
from django.test import TestCase, Client
from .views import IndexView
from django.contrib.auth import get_user_model

# Create your tests here.
class Index_Test(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
    
    def test_index_content(self):
        response = self.client.get("/")

        self.assertTemplateUsed(response, "index/index.html")
        self.assertEqual(response.status_code, 200)
    
    def test_show_login_btn(self):
        response = self.client.get("/")

        self.assertContains(response, "login")

    def test_show_logout_btn(self):
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.get("/")

        self.assertContains(response, "logout")