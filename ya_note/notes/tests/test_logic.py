from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="Петр")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            "title": "Новый заголовок",
            "text": "Новый текст",
            "slug": "new-slug",
        }

    def test_anonymous_user_cant_create_note(self):
        url = reverse("notes:add")
        notes_count_before = Note.objects.count()
        response = self.client.post(url, data=self.form_data)
        login_url = reverse("users:login")
        expected_url = f"{login_url}?next={url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_user_can_create_note(self):
        url = reverse("notes:add")
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.filter(slug=self.form_data["slug"]).first()
        self.assertIsNotNone(note)
        self.assertEqual(note.title, self.form_data["title"])
        self.assertEqual(note.text, self.form_data["text"])
        self.assertEqual(note.author, self.user)

    def test_not_unique_slug(self):
        url = reverse("notes:add")
        existing_note = Note.objects.create(
            title="Старый заголовок",
            text="Старый текст",
            slug="new-slug",
            author=self.user,
        )
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(url, data=self.form_data)
        form = response.context["form"]
        self.assertFormError(form, "slug", existing_note.slug + WARNING)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_empty_slug(self):
        url = reverse("notes:add")
        data_without_slug = {
            "title": "Новый заголовок без слаг",
            "text": "Новый текст",
        }
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(url, data=data_without_slug)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        expected_slug = slugify(data_without_slug["title"])
        note = Note.objects.filter(slug=expected_slug).first()
        assert note is not None


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username="Читатель")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title="Заголовок", text="Текст", slug="note-slug", author=cls.author
        )
        cls.form_data = {
            "title": "Обновленный заголовок",
            "text": "Обновленный текст",
            "slug": "updated-slug",
        }

    def test_author_can_delete_note(self):
        url = reverse("notes:delete", args=(self.note.slug,))
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(url)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_user_cant_delete_note_of_another_user(self):
        url = reverse("notes:delete", args=(self.note.slug,))
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_author_can_edit_note(self):
        url = reverse("notes:edit", args=(self.note.slug,))
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse("notes:success"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data["title"])
        self.assertEqual(self.note.text, self.form_data["text"])
        self.assertEqual(self.note.slug, self.form_data["slug"])

    def test_user_cant_edit_note_of_another_user(self):
        url = reverse("notes:edit", args=(self.note.slug,))
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data["title"])
