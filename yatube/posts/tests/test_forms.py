import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SanyaMochalin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа DVA',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            group=cls.group,
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text='комментарий',
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания записи в Post"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'SanyaMochalin'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_create_comment(self):
        """Проверка создания коммента в Post"""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый коммент',
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostCreateForm.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostCreateForm.post.id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый коммент',
                post=self.post,
                author=self.user,
            ).exists()
        )

    def test_comment_in_post_detail(self):
        """Проверка что коммент появился с Post_detail"""
        comment = Comment.objects.create(
            text='комментарий',
            author=self.user,
            post=self.post,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(response.context['comments'][0].text,
                         comment.text)

    def test_create_post_without_group(self):
        """Проверка создания записи в Post без группы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'SanyaMochalin'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=self.user,
                group=None
            ).exists()
        )

    def test_create_post_guest(self):
        """Проверка создания записи в Post неавторизированного пользователя"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_cant_edit_existing_slug(self):
        """Проверка прав редактирования поста"""
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostCreateForm.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateForm.post.id,
                text='Тестовый текст',
                group=self.group.id,
                author=self.user,
                pub_date=self.post.pub_date
            ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cant_edit_existing_slug_with_group(self):
        """Проверка прав редактирования поста без группы"""
        form_data = {
            'group': self.group2.id,
            'text': PostCreateForm.post.text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateForm.post.id,
                text=self.post.text,
                group=self.group2.id,
                author=self.user,
                pub_date=self.post.pub_date
            ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cant_edit_guest(self):
        """Проверка прав редактирования поста неавторизованного пользователя"""
        form_data = {
            'group': self.group.id,
            'text': PostCreateForm.post.text,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateForm.post.id,
                text=PostCreateForm.post.text,
                group=self.group.id,
                author=PostCreateForm.post.author,
                pub_date=self.post.pub_date
            ).exists())

    def test_cant_edit_not_author(self):
        """Проверка прав редактирования поста авторизованного пользователя"""
        user_not_author = User.objects.create_user(username='noname')
        authorized_client_not_author = Client()
        authorized_client_not_author.force_login(user_not_author)
        form_data = {
            'group': self.group.id,
            'text': PostCreateForm.post.text,
        }
        response = authorized_client_not_author.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostCreateForm.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/posts/{self.post.id}/')
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateForm.post.id,
                text=self.post.text,
                group=self.group.id,
                author=self.user,
                pub_date=self.post.pub_date
            ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_image(self):
        """Проверка, что при отправке поста с картинкой
        через форму PostForm редактируется запись в БД
        """
        cool_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cool_uploaded = SimpleUploadedFile(
            name='cool.gif',
            content=cool_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': PostCreateForm.post.text,
            'image': cool_uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostCreateForm.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/posts/{PostCreateForm.post.id}/')
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateForm.post.id,
                text=self.post.text,
                group=self.group.id,
                author=self.user,
                pub_date=self.post.pub_date,
                image='posts/cool.gif'
            ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_add_comment(self):
        """Проверка прав пользователя на создание комментария
        и проверка на появления комментария на странице поста
        """
        form_data = {
            'text': PostCreateForm.comment.text,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostCreateForm.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/posts/{self.post.id}/')
        self.assertTrue(
            Comment.objects.filter(
                post=PostCreateForm.post,
                text=self.comment.text,
                author=self.comment.author,
            ).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
