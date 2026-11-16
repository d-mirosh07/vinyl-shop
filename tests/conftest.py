from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from shop.models import Album, Artist, Genre


@pytest.fixture
def api_client():
    """Клієнт без авторизації."""
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="daria",
        email="daria@example.com",
        password="Capybara2026",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="sasha",
        email="sasha@example.com",
        password="Pi314159pi",
    )


@pytest.fixture
def auth_client(user):
    """Клієнт, авторизований як користувач daria."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_client(other_user):
    """Клієнт, авторизований як користувач sasha."""
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def artist(db):
    return Artist.objects.create(name="Michael Jackson")


@pytest.fixture
def genre(db):
    return Genre.objects.create(name="Pop")


@pytest.fixture
def album(artist, genre):
    return Album.objects.create(
        title="Thriller",
        price=Decimal("899.00"),
        in_stock=True,
        artist=artist,
        genre=genre,
    )
