from datetime import datetime, timedelta
import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from news.models import Comment, News


# Фикстуры пользователей и клиентов
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username="Автор")


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


# Фикстура одной базовой новости
@pytest.fixture
def news(db):
    return News.objects.create(title="Заголовок новости", text="Текст новости")


# --- НОВЫЕ ФИКСТУРЫ ДЛЯ ТЕСТОВ КОНТЕНТА ---


# Фикстура для создания пачки новостей (количество из настроек + 1)
@pytest.fixture
def bulk_news(db):
    today = datetime.today()
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто текст.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


# Фикстура для создания 10 упорядоченных по времени комментариев
@pytest.fixture
def bulk_comments(news, author):
    now = timezone.now()
    comments_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f"Текст {index}"
        )
        # Искусственно сдвигаем время создания, чтобы проверить сортировку
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


# Фикстуры для аргументов маршрутов (из прошлых уроков)
@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news, author=author, text="Текст комментария"
    )


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {"text": "Новый текст комментария"}
