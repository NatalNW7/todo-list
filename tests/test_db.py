from dataclasses import asdict

from sqlalchemy import select

from todo_list.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='jonas', password='jonas123', email='clonacartao@suporte'
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'jonas'))

    assert asdict(user) == {
        'id': 1,
        'username': new_user.username,
        'password': new_user.password,
        'email': new_user.email,
        'created_at': time,
        'updated_at': time,
    }
