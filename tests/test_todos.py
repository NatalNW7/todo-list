from http import HTTPStatus

import factory.fuzzy

from todo_list.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Test Todo', 'description': 'Test', 'state': 'draft'},
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test',
        'state': 'draft',
    }


def test_show_todos(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id)
    )
    session.commit()

    todos = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    ).json()['todos']

    assert len(todos) == expected_todos


def test_show_todos_with_pagination(session, client, user, token):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))

    todos = client.get(
        '/todos?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    ).json()['todos']

    assert len(todos) == expected_todos


def test_show_todos_filter_by_title(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, title='Test todo 1'
        )
    )

    todos = client.get(
        '/todos?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    ).json()['todos']

    assert len(todos) == expected_todos


def test_show_todos_filter_by_description(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            description='Test todo description 1',
        )
    )

    todos = client.get(
        '/todos?description=Test todo description 1',
        headers={'Authorization': f'Bearer {token}'},
    ).json()['todos']

    assert len(todos) == expected_todos


def test_show_todos_filter_by_state(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, state=TodoState.draft
        )
    )

    todos = client.get(
        '/todos?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    ).json()['todos']

    assert len(todos) == expected_todos


def test_show_todos_with_combined_filters(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='Test combined',
            description='Test combined description',
            state=TodoState.done,
        )
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Test combined 2',
            description='Test combined description 2',
            state=TodoState.todo,
        )
    )
    session.commit()

    todos = client.get(
        '/todos?title=Test combined&description=Test combined description&state=done',
        headers={'Authorization': f'Bearer {token}'},
    ).json()['todos']

    assert len(todos) == expected_todos


def test_update_todo(session, user, token, client):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste 123'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste 123'


def test_update_todo_not_found_error(session, user, token, client):
    todo = client.patch(
        '/todos/123',
        json={'title': 'teste 123'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert todo.status_code == HTTPStatus.NOT_FOUND
    assert todo.json() == {'detail': 'Task not found'}


def test_delete_todo(session, user, token, client):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_delete_todo_not_found_error(session, user, token, client):
    todo = client.delete(
        '/todos/123',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert todo.status_code == HTTPStatus.NOT_FOUND
    assert todo.json() == {'detail': 'Task not found'}
