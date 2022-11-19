from django.http import HttpResponseNotFound

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CoreURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_404(self):
        """Проверка шаблона 404.html"""
        response = self.guest_client.get(HttpResponseNotFound)
        self.assertTemplateUsed(response, 'core/404.html')
