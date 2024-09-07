from http import HTTPStatus

from fastapi.testclient import TestClient

from todo_list.app import app


def test_index():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}
