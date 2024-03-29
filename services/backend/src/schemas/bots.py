from typing import List, Optional
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import Bots
from src.schemas.features import FeaturesInSchema, FeaturesOutSchema
from pydantic import BaseModel

BaseBotInSchema = pydantic_model_creator(
    Bots, name="BotInBase", exclude=["user_id"], exclude_readonly=True)

BotOutSchema = pydantic_model_creator(
    Bots, name="Bot", exclude =[
      "modified_at", "user.password", "user.created_at", "user.modified_at", "user.oauth_tokens"
    ]
)

class BotInSchema(BaseBotInSchema):
    features: Optional[List[FeaturesInSchema]] = None


class UpdateBot(BaseModel):
    features: Optional[List[FeaturesInSchema]] = None
