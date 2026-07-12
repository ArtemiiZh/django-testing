from django.conf import settings
import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, bulk_news, home_url):
    """Количество новостей на главной странице строго ограничено."""
    response = client.get(home_url)
    object_list = response.context["object_list"]
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, bulk_news, home_url):
    """Новости на главной странице отсортированы от свежих к старым."""
    response = client.get(home_url)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, bulk_comments, detail_url):
    """Комментарии на странице детализации отсортированы по хронологии."""
    response = client.get(detail_url)
    assert "news" in response.context
    news_obj = response.context["news"]
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    "url_fixture",
    (
        pytest.lazy_fixture("detail_url"),
        pytest.lazy_fixture("edit_url"),
    ),
) 
def test_pages_contain_form(author_client, url_fixture):
    """Наличие CommentForm на страницах деталей и редактирования."""
    response = author_client.get(url_fixture)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)


def test_anonymous_client_has_no_form(client, detail_url):
    """У неавторизованного пользователя нет формы отправки комментария."""
    response = client.get(detail_url)
    assert "form" not in response.context
