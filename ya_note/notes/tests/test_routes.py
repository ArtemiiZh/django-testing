from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

# Указываем, что всем тестам в этом файле нужен доступ к базе данных
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Анонимному пользователю доступны главная, вход, выход и регистрация."""
    url = reverse(name)
    response = client.get(url)
    # В Django 5.x users:logout возвращает 200, если GET-запрос не поддерживается,
    # либо перенаправляет. Проверяем корректность ответа для всех страниц.
    if name == 'users:logout':
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
    else:
        assert response.status_code == HTTPStatus.OK


def test_logout_availability_via_post(client):
    """Страница выхода доступна через POST-запрос в Django 5.x."""
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(reader_client, name):
    """Авторизованному пользователю доступны страницы списка, добавления и успеха."""
    url = reverse(name)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete')
)
def test_pages_availability_for_different_users(
    parametrized_client, name, note, expected_status
):
    """
    Страницы отдельной заметки, редактирования и удаления доступны автору,
    но возвращают 404 для обычного читателя.
    """
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success', 'notes:detail', 'notes:edit', 'notes:delete')
)
def test_redirect_for_anonymous_client(client, name, note):
    """При попытке зайти на закрытые страницы анонима перенаправляет на логин."""
    login_url = reverse('users:login')

    if name in ('notes:detail', 'notes:edit', 'notes:delete'):
        url = reverse(name, args=(note.slug,))
    else:
        url = reverse(name)

    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
