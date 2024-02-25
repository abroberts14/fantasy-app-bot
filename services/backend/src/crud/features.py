from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Bots,Features
from src.schemas.features import FeaturesOutSchema

from src.schemas.token import Status

    
async def get_feature(feature_id) -> FeaturesOutSchema:
    return await FeaturesOutSchema.from_queryset_single(Features.get(id=feature_id))

async def get_features():
    try:
        return await FeaturesOutSchema.from_queryset(Features.all())
    except Exception as e:
        print(e)
        