from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_list.database import get_session
from todo_list.models import User
from todo_list.schemas import (
    Message,
    UserDB,
    UserResponse,
    UserSchema,
    UsersResponse,
)
from todo_list.security import get_password_hash

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
def users():
    return {'users': database}


@app.get('/users/{id}', response_model=UserResponse)
def user(id: int):
    if id > len(database) or id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    return database[id - 1]


@app.put('/users/{id}', response_model=UserResponse)
def update_user(id: int, user: UserSchema):
    if id > len(database) or id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    user_db = UserDB(**user.model_dump(), id=id)
    database[id - 1] = user_db

    return user_db


@app.delete('/users/{id}', response_model=Message)
def delete_user(id: int):
    if id > len(database) or id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User Not Found'
        )

    del database[id - 1]

    return {'message': 'User deleted'}
