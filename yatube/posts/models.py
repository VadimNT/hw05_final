from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание группы")

    class Meta:
        verbose_name = "Группа сообщества"
        verbose_name_plural = "Группы сообщества"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts", kwargs={"slug": self.slug})


class Post(CreatedModel):
    text = models.TextField(
        verbose_name="Текст поста", help_text="Введите текст поста"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите сообщество",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
        help_text="Загрузите картинку",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[: settings.NUMS_OF_SYMBOLS_POST_TEXT]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Ссылка на пост",
        related_name="comments",
        help_text="Комментарии к конкретному посту",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField(
        verbose_name="Текст комментария", help_text="Введите комментарий поста"
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписка автора",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
