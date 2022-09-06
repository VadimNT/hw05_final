import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, User, Group, Post


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class Fixture(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.not_author = User.objects.create_user(username="not_author")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-group",
            description="Тестовое описание",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый пост на пятнадцать символов",
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.uploaded.seek(0)
        cls.comment = Comment.objects.create(
            post=cls.post, author=cls.not_author, text="My comment"
        )
        cls.follow = Follow.objects.create(
            user=cls.not_author, author=cls.author
        )
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
        cls.form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)
