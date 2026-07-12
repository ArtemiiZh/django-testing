from http import HTTPStatus

from notes.tests.base import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        urls = (self.home_url, self.login_url, self.signup_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability_via_post(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (self.list_url, self.add_url, self.success_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (self.detail_url, self.edit_url, self.delete_url)
        for client, status in users_statuses:
            for url in urls:
                with self.subTest(url=url, client=client):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.add_url,
            self.success_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
