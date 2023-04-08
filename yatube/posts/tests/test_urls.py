from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_uses_correct_template_for_all(self):
        """Проверка вызываемых шаблонов """
        templates_url_names_for_all = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_names_for_all.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location_for_all(self):
        """Страницы, доступные любому пользователю"""
        templates_url_names_for_all = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': f'/profile/{PostURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.pk}/',
        }

        for address in templates_url_names_for_all.values():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_at_desired_location_for_author(self):
        """Проверка доступности страницы для автора статьи"""
        templates_url_names_for_author = {
            'posts/create_post.html':
            (f'/posts/{self.post.id}/edit/'),
        }

        for address in templates_url_names_for_author.values():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_at_desired_location_auth_user(self):
        """Проверка доступности страницы для авторизованных пользователей"""
        templates_url_names_for_auth = {
            'posts/create_post.html': '/create/',
            'posts/follow.html': '/follow/'
        }

        for address in templates_url_names_for_auth.values():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_not_exists_for_guest(self):
        """Проверка шаблона create_post.html
         для неавторизованных пользователей
         """
        response_edit = self.guest_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response_edit.status_code, HTTPStatus.FOUND)
        response_create = self.guest_client.get('/create/')
        self.assertEqual(response_create.status_code, HTTPStatus.FOUND)

    def test_url_follow_not_exists_for_guest(self):
        """Проверка шаблона follow.html
         для неавторизованных пользователей
         """
        response_follow = self.guest_client.get('/follow/')
        self.assertEqual(response_follow.status_code, HTTPStatus.FOUND)
