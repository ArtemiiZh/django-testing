from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.note = Note.objects.create(
            title="Заголовок", text="Текст", author=cls.author, slug="note-slug"
        )

    def test_pages_availability(self):
        urls = (
            ("notes:home", None),
            ("users:login", None),
            ("users:signup", None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability_via_post(self):
        url = reverse("users:logout")
        response = self.client.post(url)
        self.assertIn(response.status_code, (HTTPStatus.OK, HTTPStatus.FOUND))

    def test_pages_availability_for_auth_user(self):
        urls = (
            ("notes:list", None),
            ("notes:add", None),
            ("notes:success", None),
        )
        self.client.force_login(self.reader)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse("users:login")
        urls = (
            ("notes:list", None),
            ("notes:add", None),
            ("notes:success", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
