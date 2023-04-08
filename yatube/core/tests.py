from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CoreURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client(enforce_csrf_checks=True)

    def test_url_404(self):
        """Проверка шаблона 404.html"""
        response = self.guest_client.get('/some_invalid_url_404/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_url_403(self):
        """Проверка шаблона 403csrf.html"""
        response = self.guest_client.post('/create/')
        self.assertTemplateUsed(response, 'core/403.html')
