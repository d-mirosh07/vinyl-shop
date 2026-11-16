from decimal import Decimal

import pytest

from shop.models import Album

pytestmark = pytest.mark.django_db

ALBUMS_URL = "/api/albums/"


def detail_url(pk):
    return f"{ALBUMS_URL}{pk}/"


def album_data(artist, genre, **overrides):
    data = {
        "title": "Bad",
        "price": "599.00",
        "in_stock": True,
        "artist": artist.id,
        "genre": genre.id,
    }
    data.update(overrides)
    return data


def test_list_albums_returns_200(api_client, album):
    response = api_client.get(ALBUMS_URL)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Thriller"


def test_list_albums_search(api_client, album, artist, genre):
    Album.objects.create(
        title="Bad", price=Decimal("599.00"), artist=artist, genre=genre
    )
    response = api_client.get(ALBUMS_URL, {"search": "thr"})
    assert response.status_code == 200
    assert len(response.data) == 1


def test_create_album_authenticated_returns_201(auth_client, artist, genre):
    response = auth_client.post(ALBUMS_URL, album_data(artist, genre), format="json")
    assert response.status_code == 201
    assert Album.objects.filter(title="Bad").exists()


def test_create_album_without_auth_returns_401(api_client, artist, genre):
    response = api_client.post(ALBUMS_URL, album_data(artist, genre), format="json")
    assert response.status_code == 401
    assert Album.objects.count() == 0


def test_get_album_returns_200(api_client, album):
    response = api_client.get(detail_url(album.id))
    assert response.status_code == 200
    assert response.data["id"] == album.id


def test_get_missing_album_returns_404(api_client):
    response = api_client.get(detail_url(999))
    assert response.status_code == 404


def test_patch_album_authenticated_updates_fields(auth_client, album):
    response = auth_client.patch(
        detail_url(album.id), {"price": "799.00"}, format="json"
    )
    assert response.status_code == 200
    album.refresh_from_db()
    assert album.price == Decimal("799.00")


def test_delete_album_authenticated_returns_204(auth_client, album):
    response = auth_client.delete(detail_url(album.id))
    assert response.status_code == 204
    assert not Album.objects.filter(pk=album.id).exists()


def test_delete_missing_album_returns_404(auth_client):
    response = auth_client.delete(detail_url(999))
    assert response.status_code == 404
