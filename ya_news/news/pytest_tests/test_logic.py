from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

# Импортируем из файла с формами список стоп-слов и предупреждение формы
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

# Вешаем маркер базы данных на весь файл
pytestmark = pytest.mark.django_db


# --- ТЕСТЫ СОЗДАНИЯ КОММЕНТАРИЕВ ---


def test_anonymous_user_cant_create_comment(client, news, form_data):
    """
    Анонимный пользователь НЕ может создать комментарий
    (с проверкой редиректа).
    """
    url = reverse("news:detail", args=(news.id,))
    response = client.post(url, data=form_data)

    # Проверяем, что анонима перенаправило на страницу логина
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)

    # Проверяем, что комментарий не создался
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может успешно создать комментарий."""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=form_data)

    # Ожидаем редирект на блок комментариев страницы новости
    expected_url = f"{url}#comments"
    assertRedirects(response, expected_url)

    # Проверяем, что в базе появился ровно 1 комментарий с верными данными
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data["text"]
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """Пользователь не может использовать запрещенные слова."""
    url = reverse("news:detail", args=(news.id,))
    # Берем первое слово из списка стоп-слов (BAD_WORDS[0])
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}

    response = author_client.post(url, data=bad_words_data)

    # Проверяем ошибку валидации формы через синтаксис Django 5.x
    form = response.context['form']
    assertFormError(form, "text", WARNING)
    assert Comment.objects.count() == 0


# --- ТЕСТЫ РЕДАКТИРОВАНИЯ И УДАЛЕНИЯ КОММЕНТАРИЕВ ---


def test_author_can_delete_comment(author_client, comment, news):
    """Автор может успешно удалить свой собственный комментарий."""
    delete_url = reverse("news:delete", args=(comment.id,))
    news_url = reverse("news:detail", args=(news.id,))
    expected_url = news_url + "#comments"

    response = author_client.delete(delete_url)

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Обычный пользователь НЕ может удалить чужой комментарий."""
    delete_url = reverse("news:delete", args=(comment.id,))

    response = reader_client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, news, form_data):
    """Автор может успешно отредактировать свой собственный комментарий."""
    edit_url = reverse("news:edit", args=(comment.id,))
    news_url = reverse("news:detail", args=(news.id,))
    expected_url = news_url + "#comments"

    response = author_client.post(edit_url, data=form_data)

    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data["text"]


def test_user_cant_edit_comment_of_another_user(
    reader_client, comment, form_data
):
    """Обычный пользователь НЕ может отредактировать чужой комментарий."""
    edit_url = reverse("news:edit", args=(comment.id,))
    old_text = comment.text

    response = reader_client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
