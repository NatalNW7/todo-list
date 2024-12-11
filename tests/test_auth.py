from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time


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


def test_login_incorrect_password(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'incorrect_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_expired(client: TestClient, user):
    with freeze_time('2024-12-11 11:37'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_pass},
        )

        assert response.status_code == HTTPStatus.OK

        token = response.json()['access_token']

    with freeze_time('2024-12-11 12:08'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'test',
                'email': 'test@test.com',
                'password': 'test123',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not authenticate user'}


def test_token_refresh(client: TestClient, user, token):
    response = client.post(
        '/auth/refresh-token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data


def test_token_expired_dont_refresh(client: TestClient, user):
    with freeze_time('2024-12-11 11:37'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_pass},
        )

        assert response.status_code == HTTPStatus.OK

        token = response.json()['access_token']

    with freeze_time('2024-12-11 12:08'):
        response = client.post(
            '/auth/refresh-token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not authenticate user'}
