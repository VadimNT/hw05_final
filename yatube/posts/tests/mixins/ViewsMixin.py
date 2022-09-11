from unittest import TestCase

from django.conf import settings
from django.test import Client
from django.urls import reverse

from posts.models import Post
from posts.tests.mixins.GeneralMixin import GeneralMixin


class ViewsMixin(GeneralMixin, TestCase):
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
        cls.url_names = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": cls.group.slug}),
            reverse("posts:profile", kwargs={"username": cls.author.username}),
        ]
        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": cls.author.username}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.pk}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
