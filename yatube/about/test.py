from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/tech/"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/yech/"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
