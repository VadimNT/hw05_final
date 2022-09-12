from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.tests.mixins.ViewsMixin import ViewsMixin


class TaskCacheViewPage(ViewsMixin):
    def test_cache_index_page(self):
        """Проверка хранения кэширования страницы index."""
        response = self.guest_client.get(reverse("posts:index"))
        posts = response.content
        Post.objects.create(text="Тестовый текст", author=self.author)
        response_old = self.guest_client.get(reverse("posts:index"))
        posts_after_add = response_old.content
        self.assertEqual(
            posts_after_add, posts, "Кэшированная страница не возвращается."
        )
        cache.clear()
        response_new = self.guest_client.get(reverse("posts:index"))
        posts_new = response_new.content
        self.assertNotEqual(posts_after_add, posts_new, "Кэш не очищен.")


class TaskPagesPaginatorTests(ViewsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_list = []
        for i in range(settings.TEST_COUNT_POSTS):
            post_list.append(
                Post(
                    text=f"Тестовый текст №{i}",
                    author=cls.author,
                    group=cls.group,
                )
            )
        cls.post_paginator = Post.objects.bulk_create(post_list)

    def test_paginator_pages(self):
        """Проверка paginator на страницах index, group_list, profile"""
        for reverse_name in self.url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]),
                    settings.NUMS_OF_POSTS_ON_PAGE,
                )
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name + "?page=2")
                self.assertEqual(
                    len(response.context["page_obj"]),
                    (
                        settings.TEST_COUNT_POSTS
                        + 1
                        - settings.NUMS_OF_POSTS_ON_PAGE
                    ),
                )


class TaskPostsPagesTests(ViewsMixin):
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def check_context_info_by_response(self, response):
        if "page_obj" in response.context:
            post = response.context["page_obj"][0]
            self.check_post_info(post)
        if "post" in response.context:
            post = response.context["post"]
            self.check_post_info(post)
        if "count" in response.context:
            self.assertEqual(response.context["count"], Post.objects.count())
        if "form" in response.context:
            for value, expected in self.form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get("form").fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.check_context_info_by_response(response)

    def test_post_not_in_other_group(self):
        """Проверить, что пост не попал в группу, для которой не был
        предназначен."""
        other_group = Group.objects.create(
            title="Тестовая группа2",
            slug="test-group2",
            description="Тестовое описание2",
        )
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": other_group.slug})
        )
        self.assertFalse(response.context["page_obj"])

    def test_following_and_unfollowing_authorized_client_by_author(self):
        """Проверка подписки/отписки авторизованного пользователя
        на других пользователей"""
        before_count = Follow.objects.count()
        Follow.objects.create(user=self.author, author=self.not_author).save()
        after_count = Follow.objects.filter(author=self.not_author).count()
        self.assertEqual(
            before_count, after_count, "Подписка на автора не работает"
        )
        Follow.objects.filter(
            user=self.author, author=self.not_author
        ).delete()
        after_count = Follow.objects.filter(author=self.not_author).count()
        self.assertEqual(
            before_count - 1,
            after_count,
            "Удаление подписки на автора не работает",
        )

    def test_new_post_available_following_or_not_following(self):
        """Проверка появление поста у пользователей,
        которые подписаны на автора поста"""
        Follow.objects.create(user=self.not_author, author=self.author).save()
        Post.objects.create(
            text="Тестовый текст2", author=self.author, group=self.group
        )
        response = self.not_author_client.get(
            reverse(
                "posts:profile", kwargs={"username": self.not_author.username}
            )
        )
        print(response.context["page_obj"])
