from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_pages_uses_correct_template_for_all(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'users/login.html': reverse('users:login'),
            'users/signup.html': reverse('users:signup'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_auth(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'users/logged_out.html': reverse('users:logout'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
