import pytest

from shop.models import Artist, Genre

pytestmark = pytest.mark.django_db

ARTISTS_URL = "/api/artists/"
GENRES_URL = "/api/genres/"


def artist_url(pk):
    return f"{ARTISTS_URL}{pk}/"


def test_list_artists_returns_200(api_client, artist):
    response = api_client.get(ARTISTS_URL)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Michael Jackson"


def test_create_artist_authenticated_returns_201(auth_client):
    response = auth_client.post(ARTISTS_URL, {"name": "Queen"}, format="json")
    assert response.status_code == 201
    assert Artist.objects.filter(name="Queen").exists()


def test_create_artist_without_auth_returns_401(api_client):
    response = api_client.post(ARTISTS_URL, {"name": "Queen"}, format="json")
    assert response.status_code == 401


def test_patch_artist_authenticated_updates_name(auth_client, artist):
    response = auth_client.patch(
        artist_url(artist.id), {"name": "Michael J. Jackson"}, format="json"
    )
    assert response.status_code == 200
    artist.refresh_from_db()
    assert artist.name == "Michael J. Jackson"


def test_delete_artist_with_albums_returns_409(auth_client, album):
    response = auth_client.delete(artist_url(album.artist.id))
    assert response.status_code == 409
    assert Artist.objects.filter(pk=album.artist.id).exists()


def test_delete_artist_without_albums_returns_204(auth_client, artist):
    response = auth_client.delete(artist_url(artist.id))
    assert response.status_code == 204
    assert not Artist.objects.filter(pk=artist.id).exists()


def test_list_genres_returns_200(api_client, genre):
    response = api_client.get(GENRES_URL)
    assert response.status_code == 200
    assert len(response.data) == 1


def test_create_genre_authenticated_returns_201(auth_client):
    response = auth_client.post(GENRES_URL, {"name": "Jazz"}, format="json")
    assert response.status_code == 201
    assert Genre.objects.filter(name="Jazz").exists()


def test_models_str_representation(album, artist, genre):
    assert str(artist) == "Michael Jackson"
    assert str(genre) == "Pop"
    assert str(album) == "Thriller"
