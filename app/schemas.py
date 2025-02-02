from pydantic import BaseModel
from typing import Literal



class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class CreateTask(BaseModel):
    title: str
    description: str
    status: Literal["todo", "in_progress", "done"]