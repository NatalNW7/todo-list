from jwt import decode

from todo_list.security import create_access_token, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORIHTM]
    )

    assert decoded['test'] == data['test']
    assert decoded['exp']
