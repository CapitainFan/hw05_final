from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="anonymous")
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
            image=uploaded,
        )

        cls.user_2 = User.objects.create_user(username="anonymous2")
        cls.group_2 = Group.objects.create(
            title="Тестовый заголовок 2",
            slug="test-slug2",
            description="Тестовое описание 2",
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.user = User.objects.create_user(username="User")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """view-функция использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
        }
        for url, template in templates_pages_names.items():
            with self.subTest(url=url, template=template):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def context_on_page(self, first_object):
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_list_page_uses_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        group_post = response.context["page_obj"][0]
        self.context_on_page(group_post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        for object in response.context['page_obj']:
            post_id = object.id
            post_text = object.text
            post_author = object.author
            post_group = object.group
            self.assertEqual(post_text, self.post_list[post_id].text)
            self.assertEqual(post_author, self.user)
            self.assertEqual(post_group, self.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        first_object = response.context.get("post")
        post_id_0 = first_object.pk
        self.assertEqual(post_id_0, self.post.pk)
        post_detail = response.context.get("post")
        self.context_on_page(post_detail)

    def test_create_post(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = self.post
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": post.id})
        )
        form_fields = {
            "text": (forms.fields.CharField, post.text),
            "group": (forms.fields.ChoiceField, post.group.id),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post(self):
        """При создании пост появляется в index, group_list, profile."""
        templates_pages_names = {
            reverse("posts:index"),
            reverse("posts:group_posts", kwargs={"slug": self.group_2.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": self.user_2.username}
            ),
        }

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        post_2 = Post.objects.create(
            author=self.user_2,
            text="Тестовый текст 2",
            group=self.group_2,
            image=uploaded,
        )

        for url in templates_pages_names:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                first_object = response.context.get("page_obj")[0]
                post_author_0 = first_object.author
                post_text_0 = first_object.text
                post_group_0 = first_object.group.slug
                post_image_0 = first_object.image
                self.assertEqual(post_author_0, post_2.author)
                self.assertEqual(post_text_0, post_2.text)
                self.assertEqual(post_group_0, self.group_2.slug)
                self.assertEqual(post_image_0, post_2.image)

    def test_group_context(self):
        """Пост не попал в группу, для которой не был предназначен"""
        group_post_not_in = Group.objects.create(
            title="Группа_тест_нот_ин",
            slug="test-slug_not_in",
            description="Тест группа для поста",
        )
        group = reverse("posts:group_posts", args=[group_post_not_in.slug])
        response = self.authorized_client.get(group)
        self.assertNotIn(self.post, response.context["page_obj"])

    def test_cache(self):
        """Тестирование кэша"""
        cache_post = Post.objects.create(
            author=self.user,
            text="Тестовый текст",
        )
        response_1 = self.guest_client.get(reverse("posts:index"))
        cache_post.delete()
        response_2 = self.guest_client.get(reverse("posts:index"))
        cache.clear
        response_3 = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(
            response_1.context["page_obj"][0].text, cache_post.text
        )
        self.assertEqual(
            response_2.context["page_obj"][0].text, cache_post.text
        )
        self.assertEqual(
            response_3.context["page_obj"][0].text, self.post.text
        )


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')

    def setUp(self):
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)

    def test_follow(self):
        """Тестирование подписки"""
        self.assertFalse((Follow.objects.filter(
            user=self.user, author=self.author)).exists())
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': 'author'}))
        self.assertTrue((Follow.objects.filter(
            user=self.user, author=self.author)).exists())

    def test_unfollow(self):
        """Тестирование отписки"""
        Follow.objects.create(author=self.author, user=self.user)
        self.authorized_client.get(
            reverse("posts:profile_unfollow",
                    kwargs={'username': 'author'}))
        self.assertFalse((Follow.objects.filter(
            user=self.user, author=self.author)).exists())

    def post_follow(self):
        post = Post.objects.create(text="Текстовый текст", author=self.user)
        Follow.objects.create(author=self.author, user=self.user)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(response.context["page_obj"][0], post)

    def post_unfollow(self):
        post = Post.objects.create(
            text="Текстовый текст_2",
            author=self.user
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(post.text, response.context["page_obj"])
