from http import HTTPStatus

from django.test import Client
from django.urls import reverse

from unittest import TestCase


from posts.tests.mixins.GeneralMixin import GeneralMixin


class UrlsMixin(GeneralMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            reverse("posts:index"): ["posts/index.html", HTTPStatus.OK],
            reverse("posts:group_list", kwargs={"slug": cls.group.slug}): [
                "posts/group_list.html",
                HTTPStatus.OK,
            ],
            reverse(
                "posts:profile", kwargs={"username": cls.author.username}
            ): ["posts/profile.html", HTTPStatus.OK],
            reverse("posts:post_detail", kwargs={"post_id": cls.post.pk}): [
                "posts/post_detail.html",
                HTTPStatus.OK,
            ],
            reverse("posts:post_create"): [
                "posts/create_post.html",
                HTTPStatus.FOUND,
            ],
            reverse("posts:post_edit", kwargs={"post_id": cls.post.pk}): [
                "posts/create_post.html",
                HTTPStatus.FOUND,
            ],
            reverse("posts:follow_index"): [
                "posts/follow.html",
                HTTPStatus.FOUND,
            ],
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
