from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
        )

        for i in range(15):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_group'}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]

    def test_paginator_on_first_page(self):
        """Шаблоны на первой странице содержат 10 постов."""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse=reverse):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list), 10)

    def test_paginator_on_second_page(self):
        """Шаблоны на второй странице содержат 5 постов."""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse=reverse):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj').object_list), 5)
