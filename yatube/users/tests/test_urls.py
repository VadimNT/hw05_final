from http import HTTPStatus
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class TaskURLUsersTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.uidb64 = force_text(
            urlsafe_base64_encode(
                force_bytes(
                    self.user.pk
                )
            )
        )
        self.token = uuid4()
        self.templates_url_names = {
            reverse("users:logout"): "users/logged_out.html",
            reverse("users:signup"): "users/signup.html",
            reverse("users:login"): "users/login.html",
            reverse("users:password_reset"): "users/password_reset_form.html",
            reverse("users:password_reset_done"):
                "users/password_reset_done.html",
            reverse(
                "users:password_reset_confirm",
                kwargs={
                    "uidb64": self.uidb64,
                    "token": self.token
                },
            ): "users/password_reset_confirm.html",
            reverse("users:password_reset_complete"):
                "users/password_reset_complete.html",
        }

        self.authorized_templates_url_name = {
            reverse("users:password_change"):
                "users/password_change_form.html",
            reverse("users:password_change_done"):
                "users/password_change_done.html",
        }

    def test_authorized_client_available_page_users(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        for address in self.authorized_templates_url_name:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "Страница для пользователя недоступна",
                )

    def test_authorized_client_templates_url_name_correct_template(self):
        """Проверка использования соответствующего шаблона для
        авторизованного пользователя."""
        for address, template in self.authorized_templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response, template, "Шаблон для пользователя недоступен"
                )

    def test_guest_client_available_page_users(self):
        """Проверка доступности страниц для всех пользователей."""
        for address in self.templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    "Страница для пользователя недоступна",
                )

    def test_guest_client_urls_uses_correct_template_users(self):
        """Проверка использования соответствующего шаблона для всех
        пользователей."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, template, "Шаблон для пользователя недоступен"
                )
