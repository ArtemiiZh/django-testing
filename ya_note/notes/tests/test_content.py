from notes.forms import NoteForm
from notes.tests.base import BaseTestCase


class TestContent(BaseTestCase):

    def test_notes_list_for_different_users(self):
        clients_results = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, has_note in clients_results:
            with self.subTest(client=client):
                response = client.get(self.list_url)
                object_list = response.context["object_list"]
                self.assertEqual((self.note in object_list), has_note)

    def test_pages_contain_form(self):
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], NoteForm)
