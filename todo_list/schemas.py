from pydantic import BaseModel, ConfigDict, EmailStr

from todo_list.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UsersResponse(BaseModel):
    users: list[UserResponse]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoResponse(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoResponse]


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
