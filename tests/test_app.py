from http import HTTPStatus

from fastapi.testclient import TestClient

from todo_list.schemas import UserResponse


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
    assert response.json() == {'users': []}


def test_users_with_users(client: TestClient, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_user(client: TestClient, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get(f'/users/{user_schema['id']}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_post_username_already_exists(client: TestClient, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    del user_schema['id']
    user_schema['password'] = '123'

    responde = client.post('/users', json=user_schema)

    assert responde.status_code == HTTPStatus.BAD_REQUEST
    assert responde.json() == {'detail': 'Username already exists'}


def test_post_email_already_exists(client: TestClient, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    del user_schema['id']
    user_schema['username'] = 'Ronaldo Fenomeno'
    user_schema['password'] = '123'

    responde = client.post('/users', json=user_schema)

    assert responde.status_code == HTTPStatus.BAD_REQUEST
    assert responde.json() == {'detail': 'Email already exists'}


def test_user_not_found(client: TestClient):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_update_user(client: TestClient, user):
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


def test_update_intefrity_error(client: TestClient, user):
    fake_ronaldo = client.post(
        '/users',
        json={
            'username': 'C. Ronaldo',
            'email': 'cristiano@ronaldo.com',
            'password': 'siiuuu',
        },
    )
    fake_ronaldo = fake_ronaldo.json()

    response = client.put(
        f'users/{fake_ronaldo['id']}',
        json={
            'username': 'Ronaldo',
            'email': fake_ronaldo['email'],
            'password': 'siiuuu',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


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


def test_delete_user(client: TestClient, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client: TestClient):
    response = client.delete('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
