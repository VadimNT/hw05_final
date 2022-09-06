from django.urls import reverse

from posts.models import Comment, Post
from posts.tests.fixture import Fixture


class TaskPostsFormTests(Fixture):
    def test_create_post(self):
        """Проверка создания формы PostForm."""
        posts_count = 1
        form_data = {
            "text": "Измененный текст",
            "group": self.group.id,
            "image": self.uploaded,
        }
        response = self.author_client.post(
            reverse("posts:post_create"), data=form_data
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Измененный текст", author=self.author, group=self.group
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=form_data["group"],
                image__contains="small",
            ).exists()
        )

    def test_edit_post(self):
        """Проверка редактирования формы PostForm."""
        before_count = Post.objects.count()
        self.uploaded.seek(0)
        form_data = {
            "text": "Изменить текст",
            "group": self.group.id,
            "image": self.uploaded,
        }
        response = self.author_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        after_count = Post.objects.count()
        self.assertEqual(
            before_count,
            after_count,
            "При редактировании добавился новый пост",
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=form_data["group"],
                image__contains="small",
            ).exists()
        )

    def test_field_label(self):
        """Проверка значений field_label."""
        field_names = {"text": "Текст сообщения", "group": "Сообщество"}
        for field, value in field_names.items():
            with self.subTest(post=field):
                self.assertEqual(self.form.fields[field].label, value)

    def test_field_help_text(self):
        """Проверка значений field_help_text."""
        help_text_names = {
            "text": "Введите текст поста",
            "group": "Выберите сообщество",
            "image": "Загрузите картинку",
        }
        for field, value in help_text_names.items():
            with self.subTest(post=field):
                self.assertEqual(self.form.fields[field].help_text, value)

    def test_add_comment_non_authorized_client(self):
        """Проверка добавления комментариев неавторизованным пользователем."""
        comment_count = Comment.objects.count()
        form_data = {"text": "Мой комментарий."}
        self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(comment_count, Comment.objects.count())
        self.assertFalse(
            Comment.objects.filter(text=form_data["text"]).exists()
        )

    def test_check_add_comment(self):
        """Проверка комментирования постов авторизованным пользователем."""
        before_count = Comment.objects.count()
        form_data = {"text": "Мой комментарий."}
        response = self.author_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        after_count = Comment.objects.count()
        self.assertEqual(
            before_count + 1,
            after_count,
            "При редактировании добавился новый комментарий.",
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )
