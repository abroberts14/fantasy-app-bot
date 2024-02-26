
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import  Features, GlobalFeatures

FeaturesInSchema = pydantic_model_creator(
    Features, name="FeaturesIn", exclude=["bot_id"], exclude_readonly=True)
FeaturesOutSchema = pydantic_model_creator(
    Features, name="Features", exclude=["modified_at", "bot.user", "bot.league_id", "bot.groupme_bot_id", "bot.app" , "bot.app_id","bot.running", "bot.active", "bot.created_at", "bot.modified_at", "bot.user_id"]
)

GlobalFeaturesInSchema = pydantic_model_creator(
    GlobalFeatures, name="GlobalFeaturesIn", exclude_readonly=True)
GlobalFeaturesOutSchema = pydantic_model_creator(
    GlobalFeatures, name="GlobalFeatures", exclude=["modified_at"]
)
