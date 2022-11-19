import shutil
import tempfile
from django import forms
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SanyaMochalin')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            text='Текст',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template_for_all(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': PostPagesTests.post.author})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit',
                        kwargs={'post_id': PostPagesTests.post.id})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': PostPagesTests.post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0], self.post)

    def test_cache_index(self):
        '''Проверка кеша'''
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_group_list_page_show_correct_context(self,):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        self.assertEqual(
            response.context['group'], self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'SanyaMochalin'}
        ))
        self.assertEqual(
            response.context['author'], self.post.author)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      PostPagesTests.post.id}))
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}
        ))
        context_is_edit = response.context['is_edit']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, excepted in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, excepted)
        self.assertTrue(context_is_edit)

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        context_is_edit = response.context['is_edit']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, excepted in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, excepted)
        self.assertFalse(context_is_edit)

    def test_show_image_context(self):
        """Проверка вывода поста с картинкой"""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': PostPagesTests.post.author})
            ),
            'posts/group_list.html': (
                reverse('posts:group_list',
                        kwargs={'slug': 'test-slug'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context['page_obj'][0].image,
                                 self.post.image)

    def test_show_image_context_for_post_detail(self):
        """Проверка вывода поста с картинкой для post_detail"""
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      PostPagesTests.post.id}))
        self.assertEqual(response.context['post'].image,
                         self.post.image)


class PaginatorViewsTest(TestCase):
    NUM_TASK: int = 13
    NUM_FIRST_GROUP: int = 10
    AMOUNT_IN_FIRST_PAGE: int = 10

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
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        bilk_post: list = []
        for i in range(PaginatorViewsTest.NUM_TASK):
            if i <= PaginatorViewsTest.NUM_FIRST_GROUP:
                bilk_post.append(
                    Post(
                        text=f'Текст {i}',
                        group=cls.group,
                        author=cls.user,
                    ))
            else:
                bilk_post.append(
                    Post(
                        text=f'Текст {i}',
                        group=cls.group2,
                        author=cls.user,
                    ))
        Post.objects.bulk_create(bilk_post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        """Проверка:
        количество постов на первой странице шаблона index
        """
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(
            response.context['page_obj']), self.AMOUNT_IN_FIRST_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Проверка:
        количество постов на второй странице шаблона index
        """
        amount_second_page: int = self.NUM_TASK - self.AMOUNT_IN_FIRST_PAGE
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), amount_second_page)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка:
        количество постов на первой странице шаблона group_list
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        self.assertEqual(len(
            response.context['page_obj']), self.AMOUNT_IN_FIRST_PAGE)

    def test_group_list_second_page_contains_three_records(self):
        """Проверка:
        количество постов на второй странице шаблона group_list
        """
        amount_in_group_second_page: int = 1
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), amount_in_group_second_page)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка:
        количество постов на первой странице шаблона profile
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'SanyaMochalin'}
        ))
        self.assertEqual(len(
            response.context['page_obj']), self.AMOUNT_IN_FIRST_PAGE)

    def test_profile_second_page_contains_three_records(self):
        """Проверка:
        количество постов на второй странице шаблона profile
        """
        amount_second_page: int = self.NUM_TASK - self.AMOUNT_IN_FIRST_PAGE
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'SanyaMochalin'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), amount_second_page)
