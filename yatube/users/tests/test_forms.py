from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TaskUsersFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Проверка регистрации нового пользователя."""
        count_user = User.objects.count()
        form_data = {
            "first_name": "1st name",
            "last_name": "2nd name",
            "username": "auth",
            "email": "test@test.com",
            "password1": "20uS08er2022",
            "password2": "20uS08er2022",
        }
        self.guest_client.post(
            reverse("users:signup"), data=form_data, follow=True
        )
        self.assertEqual(User.objects.count(), count_user + 1)
