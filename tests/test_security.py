from jwt import decode

from todo_list.security import ALGORIHTM, SECRET_KEY, create_access_token


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=[ALGORIHTM])

    assert decoded['test'] == data['test']
    assert decoded['exp']
