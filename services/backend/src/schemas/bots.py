from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from src.database.models import Bots


BotInSchema = pydantic_model_creator(
    Bots, name="BotIn", exclude=["user_id"], exclude_readonly=True)
BotOutSchema = pydantic_model_creator(
    Bots, name="Bot", exclude =[
      "modified_at", "user.password", "user.created_at", "user.modified_at"
    ]
)


class UpdateBot(BaseModel):
    groupme_bot_id: Optional[str]
    name: Optional[str]
