from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models import Notes


NoteInSchema = pydantic_model_creator(
    Notes, name="NoteIn", exclude=["user_id"], exclude_readonly=True)
NoteOutSchema = pydantic_model_creator(
    Notes, name="Note", exclude =[
      "modified_at", "user.password", "user.created_at", "user.modified_at", "user.bots"
    ]
)


class UpdateNote(BaseModel):
    title: Optional[str]
    content: Optional[str]
