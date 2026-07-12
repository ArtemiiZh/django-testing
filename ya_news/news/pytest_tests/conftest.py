from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


# Группа 1: Пользователи и клиенты
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


# Группа 2: Объекты БД
@pytest.fixture
def news(db):
    return News.objects.create(title="Заголовок новости", text="Текст новости")


@pytest.fixture
def bulk_news(db):
    today = datetime.today()
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто text.",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news, author=author, text="Текст комментария"
    )


@pytest.fixture
def bulk_comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment_obj = Comment.objects.create(
            news=news, author=author, text=f"Текст {index}"
        )
        comment_obj.created = now + timedelta(days=index)
        comment_obj.save()


# Группа 3: Централизованные фикстуры-маршруты URL
@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def login_url():
    return reverse("users:login")


@pytest.fixture
def logout_url():
    return reverse("users:logout")


@pytest.fixture
def signup_url():
    return reverse("users:signup")


@pytest.fixture
def detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse("news:delete", args=(comment.id,))
