from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()


def test_about_author_url_exists_at_desired_location(self):
    """Страница "/about/author/" доступна любому пользователю."""
    response = self.guest_client.get('/about/author/')
    self.assertEqual(response.status_code, 200)


def test_about_tech_url_exists_at_desired_location(self):
    """Страница "/about/tech/" доступна любому пользователю."""
    response = self.guest_client.get('/about/tech/')
    self.assertEqual(response.status_code, 200)
