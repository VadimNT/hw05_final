from http import HTTPStatus

from django.urls import reverse

from posts.tests.mixins.UrlsMixin import UrlsMixin


class TaskURLPostTests(UrlsMixin):
    def test_access_edit_post_other_author(self):
        """Проверка доступности редактирования поста другому автору"""
        response = self.not_author_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            "Пользователь не перенаправляется на другую страницу",
        )

        self.assertEqual(
            response.url,
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            "Отображается другая страница, не соответствующая ТЗ",
        )

    def test_unexisting_page_url(self):
        """Проверка не сущетвующей страницы."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_available_page_posts(self):
        """Проверка доступности страниц."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    template[1],
                    "Страница для неавторизованного пользователя недоступна",
                )

    def test_urls_uses_correct_template_posts(self):
        """Проверка использования соответствующего шаблона."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template[0],
                    "Страница для автора поста недоступна",
                )
