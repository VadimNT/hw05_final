from unittest import TestCase

from django.test import Client


from posts.forms import PostForm
from posts.tests.mixins.GeneralMixin import GeneralMixin


class FormsMixin(GeneralMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
