from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

# Вешаем маркер базы данных на весь файл
pytestmark = pytest.mark.django_db


# 1. ПОЛНОСТЬЮ ОПТИМИЗИРОВАННЫЙ ТЕСТ: Доступность страниц (без if/else)
@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("client"), HTTPStatus.OK),  # Аноним
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),  # Автор
        (pytest.lazy_fixture("reader_client"), HTTPStatus.OK),  # Читатель
    ),
)
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:home", None),
        ("users:login", None),
        ("users:signup", None),
        (
            "news:detail",
            pytest.lazy_fixture("news_id_for_args"),
        ),
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, expected_status, name, args
):
    # args принимает либо None, либо кортеж с ID
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# 2. Доступность редактирования и удаления комментария
@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (pytest.lazy_fixture("reader_client"), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_comment_edit_and_delete_availability(
    parametrized_client, expected_status, name, args
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# 3. Тест редиректов анонима на страницу логина
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse("users:login")
    url = reverse(name, args=args)
    expected_redirect = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_redirect)


# 4. Проверка logout через POST
def test_logout_availability(client):
    url = reverse("users:logout")
    response = client.post(url)
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
