from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todo_list.database import get_session
from todo_list.models import User
from todo_list.schemas import (
    Message,
    Token,
    UserResponse,
    UserSchema,
    UsersResponse,
)
from todo_list.security import (
    check_password,
    create_access_token,
    get_current_user,
    get_password_hash,
)

app = FastAPI()


@app.get('/', response_model=Message)
def index():
    return {'message': 'Hello, World!'}


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    user_db = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif user_db.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    user_db = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@app.get('/users', response_model=UsersResponse)
def users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{id}', response_model=UserResponse)
def user(id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    return user


@app.put('/users/{id}', response_model=UserResponse)
def update_user(
    id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    curret_user: User = Depends(get_current_user),
):
    if curret_user != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        curret_user.username = user.username
        curret_user.password = get_password_hash(user.password)
        curret_user.email = user.email
        session.commit()
        session.refresh(curret_user)

        return curret_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@app.delete('/users/{id}', response_model=Message)
def delete_user(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    if not check_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
