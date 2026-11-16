import pytest

from shop.models import Wishlist

pytestmark = pytest.mark.django_db

WISHLIST_URL = "/api/wishlist/"


def wishlist_item_url(pk):
    return f"{WISHLIST_URL}{pk}/"


def test_wishlist_without_auth_returns_401(api_client):
    response = api_client.get(WISHLIST_URL)
    assert response.status_code == 401


def test_add_to_wishlist_success(auth_client, user, album):
    response = auth_client.post(WISHLIST_URL, {"album": album.id}, format="json")
    assert response.status_code == 201
    assert Wishlist.objects.filter(user=user, album=album).exists()


def test_list_wishlist_returns_only_own_albums(auth_client, other_client, album, user):
    auth_client.post(WISHLIST_URL, {"album": album.id}, format="json")
    response = auth_client.get(WISHLIST_URL)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == album.id


def test_add_unknown_album_returns_404(auth_client):
    response = auth_client.post(WISHLIST_URL, {"album": 999}, format="json")
    assert response.status_code == 404


def test_remove_from_wishlist_success(auth_client, user, album):
    Wishlist.objects.create(user=user, album=album)
    response = auth_client.delete(wishlist_item_url(album.id))
    assert response.status_code == 204
    assert not Wishlist.objects.filter(user=user, album=album).exists()


def test_remove_nonexistent_item_returns_404(auth_client, album):
    response = auth_client.delete(wishlist_item_url(album.id))
    assert response.status_code == 404
