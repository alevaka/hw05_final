import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            image=uploaded,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTemplateUsed(response, 'posts/index.html')

        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index, group_list, profile
        сформирован с правильным контекстом."""

        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]

        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context.get('page_obj').object_list[0]
                post_author_0 = first_object.author.username
                post_text_0 = first_object.text
                post_group_0 = first_object.group.title
                post_image_0 = first_object.image
                self.assertEqual(post_author_0, 'HasNoName')
                self.assertEqual(post_text_0, 'Тестовый текст')
                self.assertEqual(post_group_0, 'Тестовая группа')
                self.assertEqual(post_image_0, 'posts/small.gif')

    def test_details_page_show_correct_context(self):
        """Шаблон details сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response.context.get('post')
        post_author_0 = post.author.username
        post_text_0 = post.text
        post_group_0 = post.group.title
        post_image_0 = post.image
        self.assertEqual(post_author_0, 'HasNoName')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, None)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_check_post_not_in_group(self):
        self.another_group = Group.objects.create(
            title='Другая группа',
            slug='another_group',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'another_group'}))
        object_list = response.context.get('page_obj').object_list
        self.assertEqual(len(object_list), 0)

    def test_index_page_cache(self):
        """Тестирование кэширования главной страницы"""
        self.cached_post = Post.objects.create(
            author=self.user,
            text='Тестовый текст кэширования',
            group=self.group,
        )
        cache.clear()
        response_add = self.authorized_client.get(reverse('posts:index'))
        self.cached_post.delete()
        response_del = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_add.content, response_del.content)
        cache.clear()

    def test_authorized_user_follow(self):
        """Тестирование подписки на автора"""
        self.author = User.objects.create(username='NoNameAuthor')
        follow_count_before = self.user.follower.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.assertEqual(self.user.follower.count(), follow_count_before + 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )

    def test_authorized_user_unfollow(self):
        """Тестирование отписки на автора"""
        self.author = User.objects.create(username='NoNameAuthor')
        follow_count_before = self.user.follower.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        self.assertEqual(self.user.follower.count(), follow_count_before)

    def test_follow_page(self):
        """Проверка, что пост появляется у того, кто на него подписан.
        И не появляется у тех, кто не подписан"""
        self.author = User.objects.create(username='NoNameAuthor')
        # self.another_user = User.objects.create(username='AnotherUser')
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        self.follow_post = Post.objects.create(
            author=self.author,
            text='Тестовый текст подписки',
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.context.get(
            'page_obj').object_list[0].text, 'Тестовый текст подписки'
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context.get('page_obj').object_list.count(), 0
        )
