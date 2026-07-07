import pytest
from django.conf import settings
from django.urls import reverse

# Вешаем маркер базы данных на весь файл
pytestmark = pytest.mark.django_db


# --- ТЕСТЫ ГЛАВНОЙ СТРАНИЦЫ ---

# 1. Количество новостей на главной
def test_news_count(client, bulk_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


# 2. Сортировка новостей на главной
def test_news_order(client, bulk_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# --- ТЕСТЫ СТРАНИЦЫ ДЕТАЛЕЙ НОВОСТИ ---

# 3. Сортировка комментариев
def test_comments_order(client, news, bulk_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


# 4. Проверка наличия формы для авторизованного автора на разных страницах
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_pages_contain_form(author_client, name, args):
    from news.forms import CommentForm
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


# 5. Проверка, что у анонима формы на странице новости точно НЕТ
def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
