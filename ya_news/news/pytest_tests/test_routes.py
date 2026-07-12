from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf
import pytest

pytestmark = pytest.mark.django_db

# Локальные лаконичные константы
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "url_fixture, parametrized_client, expected_status",
    (
        (lf("home_url"), lf("client"), OK),
        (lf("login_url"), lf("client"), OK),
        (lf("signup_url"), lf("client"), OK),
        (lf("detail_url"), lf("client"), OK),
        (lf("edit_url"), lf("author_client"), OK),
        (lf("edit_url"), lf("reader_client"), NOT_FOUND),
        (lf("delete_url"), lf("author_client"), OK),
        (lf("delete_url"), lf("reader_client"), NOT_FOUND),
    ),
)
def test_pages_availability_via_get(
    url_fixture, parametrized_client, expected_status
):
    """Объединенный тест статус-кодов GET-запросов для всех роутов.""" 
    response = parametrized_client.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture, parametrized_client, expected_status",
    (
        # Исправлено: Django возвращает статус 200 на POST-запрос разлогирования
        (lf("logout_url"), lf("client"), OK),
    ),
)
def test_pages_availability_via_post(url_fixture, parametrized_client, expected_status):
    """Объединенный тест статус-кодов POST-запросов с точным ожиданием."""
    response = parametrized_client.post(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture",
    (
        lf("edit_url"),
        lf("delete_url"),
    ),
)
def test_redirect_for_anonymous_client(client, url_fixture, login_url):
    """Проверка перенаправления анонимных пользователей."""
    expected_redirect = f"{login_url}?next={url_fixture}"
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect)
