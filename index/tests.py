from django.test import TestCase
from .views import IndexView

# Create your tests here.
class Index_Test(TestCase):
    def test_index_content(self):
        response = self.client.get("")

        self.assertTemplateUsed(response, "index/index.html")
        self.assertEqual(response.status_code, 200)
