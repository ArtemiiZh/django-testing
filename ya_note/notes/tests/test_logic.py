from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.base import BaseTestCase


class TestLogic(BaseTestCase):


    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f"{self.login_url}?next={self.add_url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data["title"])
        self.assertEqual(note.text, self.form_data["text"])
        self.assertEqual(note.slug, self.form_data["slug"])
        self.assertEqual(note.author, self.author)

    def test_not_unique_slug(self):
        # Используем слаг уже существующей в BaseTestCase заметки
        self.form_data["slug"] = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)

        # Сначала проверяем количество, затем — форму
        self.assertEqual(Note.objects.count(), notes_count_before)
        form = response.context["form"]
        self.assertFormError(form, "slug", self.note.slug + WARNING)

    def test_empty_slug_generates_automatically(self):
        data_without_slug = {
            "title": "Новый заголовок без слаг",
            "text": "Новый текст",
        }
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=data_without_slug)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        expected_slug = slugify(data_without_slug["title"])
        note = Note.objects.get()
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(BaseTestCase):

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_user_cant_delete_foreign_note(self):
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        # Забираем объект из БД заново по ID (вместо refresh_from_db)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data["title"])
        self.assertEqual(updated_note.text, self.form_data["text"])
        self.assertEqual(updated_note.slug, self.form_data["slug"])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # Проверяем, что все поля остались прежними
        db_note = Note.objects.get(id=self.note.id)
        self.assertEqual(db_note.title, self.note.title)
        self.assertEqual(db_note.text, self.note.text)
        self.assertEqual(db_note.slug, self.note.slug)
        self.assertEqual(db_note.author, self.note.author)
