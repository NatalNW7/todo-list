from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_list.database import get_session
from todo_list.models import Todo, User
from todo_list.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoResponse,
    TodoSchema,
    TodoUpdate,
)
from todo_list.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])


@router.post('/', response_model=TodoResponse)
def create_todo(
    todo: TodoSchema,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    todo_db = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(todo_db)
    session.commit()
    session.refresh(todo_db)

    return todo_db


@router.get('/', response_model=TodoList)
def show_todos(
    todo_filter: Annotated[FilterTodo, Query()],
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    ).all()

    return {'todos': todos}


@router.patch('/{id}', response_model=TodoResponse)
def update_todo(
    id: int,
    todo: TodoUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    todo_db = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    for key, valeu in todo.model_dump(exclude_unset=True).items():
        setattr(todo_db, key, valeu)

    session.add(todo_db)
    session.commit()
    session.refresh(todo_db)

    return todo_db


@router.delete('/{id}', response_model=Message)
def delete_todo(
    id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    session.delete(todo)
    session.commit()

    return {'message': 'Task has been deleted successfully'}
