from http import HTTPStatus

from fastapi.testclient import TestClient

from todo_list.schemas import UserResponse


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


def test_update_user(client: TestClient, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Ronaldo Fenomeno',
            'email': 'ronaldofenomeno@email.com',
            'password': '4321',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Ronaldo Fenomeno',
        'email': 'ronaldofenomeno@email.com',
        'id': user.id,
    }


def test_update_user_integrity_error(client: TestClient, user):
    fake_ronaldo = client.post(
        '/users',
        json={
            'username': 'C. Ronaldo',
            'email': 'cr7@fakeronaldo.com',
            'password': 'siiuuu',
        },
    ).json()

    token = client.post(
        '/auth/token',
        data={'username': fake_ronaldo['email'], 'password': 'siiuuu'},
    ).json()['access_token']

    response = client.put(
        f'/users/{fake_ronaldo['id']}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Ronaldo',
            'email': 'cr7@fakeronaldo.com',
            'password': 'siiuuu',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_user_not_enough_permisson_error(client: TestClient, user):
    fake_ronaldo = client.post(
        '/users',
        json={
            'username': 'C. Ronaldo',
            'email': 'cr7@fakeronaldo.com',
            'password': 'siiuuu',
        },
    ).json()

    token = client.post(
        '/auth/token',
        data={'username': fake_ronaldo['email'], 'password': 'siiuuu'},
    ).json()['access_token']

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Ronaldo',
            'email': 'cr7@fakeronaldo.com',
            'password': 'siiuuu',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client: TestClient, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_enough_permisson_error(
    client: TestClient, user, token
):
    response = client.delete(
        '/users/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
