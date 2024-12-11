from jwt import decode

from todo_list.security import create_access_token, settings, get_current_user


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORIHTM]
    )

    assert decoded['test'] == data['test']
    assert decoded['exp']
