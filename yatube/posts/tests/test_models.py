from django.conf import settings

from .mixins.GeneralMixin import GeneralMixin
from ..models import Group, Post


class TaskModelTest(GeneralMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_models_have_correct_object_names(self):
        post = Post.objects.latest("id")
        group = Group.objects.latest("id")

        self.assertEqual(
            str(post),
            self.post.text[: settings.NUMS_OF_SYMBOLS_POST_TEXT],
            "Метод __str__ для модели Post не работает",
        )

        self.assertEqual(
            str(group),
            self.group.title,
            "Метод __str__ для модели Group не работает",
        )

    def check_verbose_name(self, object_model, field_verboses):
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    object_model._meta.get_field(value).verbose_name,
                    expected,
                    f'"Значение verbose_name для модели {type(object_model)}'
                    f' не установлено или не соответствует ТЗ"',
                )

    def check_help_text(self, object_model, help_text):
        for value, expected in help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    object_model._meta.get_field(value).help_text,
                    expected,
                    f'"Значение help_text для модели {type(object_model)}'
                    f' не установлено или не соответствует ТЗ"',
                )

    def test_verbose_name(self):
        """Проверка правильности значения verbose_name в модели Post"""
        field_verboses_model = {
            self.post: {
                "text": "Текст поста",
                "pub_date": "Дата публикации",
                "author": "Автор",
                "group": "Группа",
                "image": "Картинка",
            },
            self.group: {
                "title": "Название группы",
                "slug": "URL",
                "description": "Описание группы",
            },
            self.comment: {
                "post": "Ссылка на пост",
                "author": "Автор",
                "text": "Текст комментария",
            },
            self.follow: {"user": "Подписчик", "author": "Подписка автора"},
        }
        for object_model, field_verboses in field_verboses_model.items():
            self.check_verbose_name(object_model, field_verboses)

    def test_help_text(self):
        help_text_model = {
            self.post: {
                "text": "Введите текст поста",
                "group": "Выберите сообщество",
                "image": "Загрузите картинку",
            },
            self.comment: {
                "post": "Комментарии к конкретному посту",
                "text": "Введите комментарий поста",
            },
        }
        for object_model, help_text in help_text_model.items():
            self.check_help_text(object_model, help_text)
