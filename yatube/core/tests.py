from django.contrib.auth import get_user_model
from django.http import (HttpResponseForbidden, HttpResponseNotFound,
                         HttpResponseServerError)
from django.test import Client, TestCase

User = get_user_model()


class CoreURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_url_404(self):
        """Проверка шаблона 404.html"""
        response = self.guest_client.get(HttpResponseNotFound)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_url_403(self):
        """Проверка шаблона 403csrf.html"""
        response = self.guest_client.get(HttpResponseForbidden)
        self.assertTemplateUsed(response, 'core/403csrf.html')

    def test_url_500(self):
        """Проверка шаблона 500.html"""
        response = self.guest_client.get(HttpResponseServerError)
        self.assertTemplateUsed(response, 'core/500.html')
