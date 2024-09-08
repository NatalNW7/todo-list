from http import HTTPStatus

from fastapi.testclient import TestClient


def test_index(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_create_user(client: TestClient):
    response = client.post(
        '/users',
        json={
            'username': 'test_user',
            'email': 'test_user@email.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'test_user',
        'email': 'test_user@email.com',
        'id': 1,
    }


def test_users(client: TestClient):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'test_user',
                'email': 'test_user@email.com',
                'id': 1,
            }
        ]
    }


def test_user(client: TestClient):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test_user',
        'email': 'test_user@email.com',
        'id': 1,
    }


def test_user_not_found(client: TestClient):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_update_user(client: TestClient):
    response = client.put(
        '/users/1',
        json={
            'username': 'new_test_user',
            'email': 'new_test_user@email.com',
            'password': '4321',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'new_test_user',
        'email': 'new_test_user@email.com',
        'id': 1,
    }


def test_update_user_not_found(client: TestClient):
    response = client.put(
        '/users/2',
        json={
            'username': 'new_test_user',
            'email': 'new_test_user@email.com',
            'password': '4321',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user(client: TestClient):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client: TestClient):
    response = client.delete('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
