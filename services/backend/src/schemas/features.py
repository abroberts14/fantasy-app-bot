
from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import  Features, BotFeatures

FeaturesInSchema = pydantic_model_creator(
    Features, name="FeaturesIn", exclude_readonly=True)
FeaturesOutSchema = pydantic_model_creator(
    Features, name="Features", exclude=["modified_at"]
)

BotFeaturesInSchema = pydantic_model_creator(
    BotFeatures, name="BotFeaturesIn", exclude_readonly=True)
BotFeaturesOutSchema = pydantic_model_creator(
    BotFeatures, name="BotFeatures", exclude=["modified_at"]
)
