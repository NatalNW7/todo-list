from http import HTTPStatus

from fastapi.testclient import TestClient


def test_login(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_pass},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_login_incorrect_email(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': 'incorrect@email.com', 'password': user.clean_pass},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_password_email(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'incorrect_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
