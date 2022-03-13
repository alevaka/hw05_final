import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif_1,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_edit_old_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'New text',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'New text')
        self.assertEqual(Post.objects.get(id=self.post.id).group, self.group)

    def test_unregistered_user_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, 200)

    def test_unregistered_user_edit_old_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'New text',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(Post.objects.get(id=self.post.id).text,
                         'Тестовый текст')
        self.assertEqual(Post.objects.get(id=self.post.id).group, self.group)

    def test_unregistered_user_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertEqual(response.status_code, 200)

    def test_registered_user_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(response.context.get(
            'comments')[0].text, 'Тестовый текст комментария'
        )
