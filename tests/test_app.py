from http import HTTPStatus

from fastapi.testclient import TestClient


def test_index(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_login(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_pass},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
