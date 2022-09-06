from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.templates_url_names = {
            reverse("about:author"): "about/author.html",
            reverse("about:tech"): "about/tech.html",
        }

    def test_available_page_about(self):
        """Проверка доступности страниц."""
        for address in self.templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "Страница для неавторизованного пользователя недоступна",
                )

    def test_urls_uses_correct_template_about(self):
        """Проверка использования соответствующего шаблона."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    "Страница для автора поста недоступна",
                )
