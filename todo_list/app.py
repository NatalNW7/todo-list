from http import HTTPStatus

from fastapi import FastAPI

from todo_list.routers import auth, todos, users
from todo_list.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def index():
    return {'message': 'Hello, World!'}
