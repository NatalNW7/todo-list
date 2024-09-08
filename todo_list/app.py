from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from .schemas import Message, User, UserDB, UserResponse, UsersResponse

app = FastAPI()


database = []


@app.get('/', response_model=Message)
def index():
    return {'message': 'Hello, World!'}


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: User):
    user_db = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_db)

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
def update_user(id: int, user: User):
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
