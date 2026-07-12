import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from notes.models import Note

User = get_user_model()


@pytest.fixture
def author():
    """Фикстура автора заметки."""
    return User.objects.create(username='Автор')


@pytest.fixture
def reader():
    """Фикстура обычного читателя."""
    return User.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Клиент, в котором авторизован автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Клиент, в котором авторизован читатель."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def note(author):
    """Фикстура создания заметки."""
    return Note.objects.create(
        title='Заголовок',
        text='Текст заметок',
        slug='note-slug',
        author=author
    )


@pytest.fixture
def form_data():
    """Данные для форм создания и редактирования заметок."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }
