from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор заметок")
        cls.reader = User.objects.create(username="Просто читатель")
        cls.note = Note.objects.create(
            title="Заголовок теста",
            text="Текст теста",
            author=cls.author,
            slug="test-slug",
        )

    def test_notes_list_for_different_users(self):
        users_results = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse("notes:list")
        for user, has_note in users_results:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context["object_list"]
                self.assertEqual((self.note in object_list), has_note)

    def test_pages_contain_form(self):
        urls = (
            ("notes:add", None),
            ("notes:edit", (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], NoteForm)
