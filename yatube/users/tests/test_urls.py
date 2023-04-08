from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_urls_uses_correct_template_for_all(self):
        """Проверка вызываемых шаблонов для неавторизованного пользователя"""
        templates_url_names_for_all = {
            'users/login.html': '/auth/login/',
            'users/signup.html': '/auth/signup/',
        }

        for template, address in templates_url_names_for_all.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_auth(self):
        """Проверка вызываемых шаблонов для авторизованного пользователя"""
        templates_url_names_for_all = {
            'users/logged_out.html': '/auth/logout/',
        }

        for template, address in templates_url_names_for_all.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
