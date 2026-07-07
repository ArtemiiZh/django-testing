from http import HTTPStatus
import pytest
from django.urls import reverse
from pytils.translit import slugify
from pytest_django.asserts import assertRedirects, assertFormError

from notes.forms import WARNING
from notes.models import Note

# Включаем доступ к базе данных для всех тестов логики
pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_note(client, form_data):
    """
    Анонимный пользователь не может создать заметку
    и перенаправляется на логин.
    """
    url = reverse('notes:add')
    notes_count_before = Note.objects.count()
    response = client.post(url, data=form_data)

    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == notes_count_before


def test_user_can_create_note(author_client, author, form_data):
    """Авторизованный пользователь может успешно создать заметку."""
    url = reverse('notes:add')
    notes_count_before = Note.objects.count()
    response = author_client.post(url, data=form_data)

    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == notes_count_before + 1

    # Находим созданную заметку и сверяем поля
    note = Note.objects.filter(slug=form_data['slug']).first()
    assert note is not None
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.author == author


def test_not_unique_slug(author_client, note, form_data):
    """Нельзя создать заметку со слагом, который уже существует в базе."""
    url = reverse('notes:add')
    # Принудительно делаем слаг в форме таким же, как у существующей заметки
    form_data['slug'] = note.slug
    notes_count_before = Note.objects.count()
    response = author_client.post(url, data=form_data)

    # Достаем форму из контекста и проверяем ошибку через assertFormError
    form = response.context['form']
    assertFormError(form, 'slug', note.slug + WARNING)
    assert Note.objects.count() == notes_count_before


def test_empty_slug(author_client, form_data):
    """Если слаг пустой, он генерируется из заголовка (title)."""
    url = reverse('notes:add')
    notes_count_before = Note.objects.count()
    # Удаляем слаг из данных формы
    form_data.pop('slug')
    response = author_client.post(url, data=form_data)

    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == notes_count_before + 1

    # Вычисляем ожидаемый слаг и проверяем его наличие в базе
    expected_slug = slugify(form_data['title'])
    note = Note.objects.filter(slug=expected_slug).first()
    assert note is not None


def test_author_can_delete_note(author_client, note):
    """Автор может успешно удалить свою заметку."""
    url = reverse('notes:delete', args=(note.slug,))
    notes_count_before = Note.objects.count()
    response = author_client.delete(url)

    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == notes_count_before - 1


def test_user_cant_delete_note_of_another_user(reader_client, note):
    """Обычный читатель не может удалить чужую заметку (получает 404)."""
    url = reverse('notes:delete', args=(note.slug,))
    notes_count_before = Note.objects.count()
    response = reader_client.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == notes_count_before


def test_author_can_edit_note(author_client, note, form_data):
    """Автор может успешно отредактировать свою заметку."""
    url = reverse('notes:edit', args=(note.slug,))
    response = author_client.post(url, data=form_data)

    assertRedirects(response, reverse('notes:success'))
    # Обновляем объект из базы данных
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_user_cant_edit_note_of_another_user(reader_client, note, form_data):
    """Обычный читатель не может редактировать чужую заметку (получает 404)."""
    url = reverse('notes:edit', args=(note.slug,))
    response = reader_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверяем, что поля заметки в базе НЕ изменились
    note.refresh_from_db()
    assert note.title != form_data['title']
