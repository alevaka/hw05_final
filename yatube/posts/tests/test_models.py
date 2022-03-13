from django.contrib.auth import get_user_model
from django.test import TestCase


from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовая пост',
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        test_str_group = PostModelTest.group.__str__()
        self.assertEqual(test_str_group, PostModelTest.group.title)
        test_str_post = PostModelTest.post.__str__()
        self.assertEqual(test_str_post, PostModelTest.post.text[:15])
