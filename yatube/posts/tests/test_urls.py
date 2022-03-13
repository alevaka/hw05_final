from django.test import Client, TestCase

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.user_1 = User.objects.create(username='HasNoName_1')
        cls.post_1 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый текст 1',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        # self.user = User.objects.create(username='HasNoName')
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_templates_unauthorized(self):
        template_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_status_codes_unauthorized(self):
        status_codes_url = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user.username}/': 200,
            f'/posts/{self.post.id}/': 200,
            f'/posts/{self.post.id}/edit/': 302,
            '/posts/create/': 404,
            'unexisting_page': 404,
        }
        for address, status_code in status_codes_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_templates_authorized(self):
        template_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_status_codes_authorized(self):
        status_codes_url = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user.username}/': 200,
            f'/posts/{self.post.id}/': 200,
            f'/posts/{self.post.id}/edit/': 200,
            f'/posts/{self.post_1.id}/edit/': 302,
            '/posts/create/': 404,
            '/unexisting_page/': 404,
        }
        for address, status_code in status_codes_url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_code)
