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
            author=cls.user,
            text='Тестовая группа номер 1',
        )

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text, str(post))

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        group_title = group.title
        self.assertEqual(group_title, str(group))
