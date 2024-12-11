from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from todo_list.database import get_session
from todo_list.models import Todo, User
from todo_list.schemas import TodoResponse, TodoSchema
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
