from django import forms
from django.test import Client, TestCase
from django.urls import reverse


class TaskUsersPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("users:signup"))
        form_fields = {
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": forms.fields.CharField,
            "email": forms.fields.EmailField,
            "password1": forms.fields.CharField,
            "password2": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
