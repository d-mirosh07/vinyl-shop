import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
REFRESH_URL = "/api/auth/refresh/"


@pytest.fixture
def register_data():
    return {
        "username": "roma",
        "email": "roma@example.com",
        "password": "Password123!",
        "password2": "Password123!",
    }


def test_register_success(api_client, register_data):
    response = api_client.post(REGISTER_URL, register_data, format="json")
    assert response.status_code == 201
    assert response.data["username"] == "roma"
    assert User.objects.filter(username="roma").exists()


def test_register_password_mismatch(api_client, register_data):
    register_data["password2"] = "WrongPassword99!"
    response = api_client.post(REGISTER_URL, register_data, format="json")
    assert response.status_code == 400
    assert not User.objects.filter(username="roma").exists()


def test_register_with_weak_password(api_client, register_data):
    register_data["password"] = "123"
    register_data["password2"] = "123"
    response = api_client.post(REGISTER_URL, register_data, format="json")
    assert response.status_code == 400
    assert "password" in response.data


def test_login_success(api_client, user):
    response = api_client.post(
        LOGIN_URL, {"username": "daria", "password": "Capybara2026"}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data


def test_login_wrong_password(api_client, user):
    response = api_client.post(
        LOGIN_URL, {"username": "daria", "password": "wrong"}, format="json"
    )
    assert response.status_code == 401


def test_refresh_token_success(api_client, user):
    login = api_client.post(
        LOGIN_URL, {"username": "daria", "password": "Capybara2026"}, format="json"
    )
    response = api_client.post(
        REFRESH_URL, {"refresh": login.data["refresh"]}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data
