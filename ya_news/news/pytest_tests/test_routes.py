from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

# Вешаем маркер базы данных на весь файл
pytestmark = pytest.mark.django_db


# 1. ПОЛНОСТЬЮ ОПТИМИЗИРОВАННЫЙ ТЕСТ: Доступность страниц (без if/else)
@pytest.mark.parametrize(
    "url_fixture, parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("home_url"),
         pytest.lazy_fixture("client"), HTTPStatus.OK),
        (pytest.lazy_fixture("login_url"),
         pytest.lazy_fixture("client"), HTTPStatus.OK),
        (pytest.lazy_fixture("signup_url"),
         pytest.lazy_fixture("client"), HTTPStatus.OK),
        (pytest.lazy_fixture("detail_url"),
         pytest.lazy_fixture("client"), HTTPStatus.OK),
        (pytest.lazy_fixture("edit_url"),
         pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (pytest.lazy_fixture("edit_url"),
         pytest.lazy_fixture("reader_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("delete_url"),
         pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (pytest.lazy_fixture("delete_url"),
         pytest.lazy_fixture("reader_client"), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_via_get(
    url_fixture, parametrized_client, expected_status
):
    """Объединенный тест статус-кодов GET-запросов для всех роутов."""
    response = parametrized_client.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture, parametrized_client",
    (
        (
            pytest.lazy_fixture("logout_url"),
            pytest.lazy_fixture("client"),
        ),
    ),
)
def test_pages_availability_via_post(url_fixture, parametrized_client):
    """Объединенный тест статус-кодов POST-запросов (например, logout)."""
    response = parametrized_client.post(url_fixture)
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.parametrize(
    "url_fixture",
    (
        pytest.lazy_fixture("edit_url"),
        pytest.lazy_fixture("delete_url"),
    ),
)
def test_redirect_for_anonymous_client(client, url_fixture, login_url):
    """Проверка перенаправления анонимных пользователей."""
    expected_redirect = f"{login_url}?next={url_fixture}"
    response = client.get(url_fixture)
    assertRedirects(response, expected_redirect)
