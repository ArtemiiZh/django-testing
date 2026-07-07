import pytest
from django.urls import reverse

from notes.forms import NoteForm

# Включаем доступ к базе данных для всех тестов контента
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('reader_client'), False),
    )
)
def test_notes_list_for_different_users(
    parametrized_client, note_in_list, note
):
    """Автор видит свою заметку в списке, а другой читатель — нет."""
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', pytest.lazy_fixture('note')),
    )
)
def test_pages_contain_form(author_client, name, args):
    """На страницах добавления и редактирования заметки
    автору доступна форма."""
    if args:
        url = reverse(name, args=(args.slug,))
    else:
        url = reverse(name)

    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)
