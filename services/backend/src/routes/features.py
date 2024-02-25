from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist, IntegrityError

from src.auth.jwthandler import get_current_user
from src.schemas.features import FeaturesOutSchema
from src.schemas.token import Status
from src.schemas.users import UserOutSchema
import src.crud.features as crud
router = APIRouter()


@router.get(
    "/feature/{id}",
    response_model=FeaturesOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def get_bot(id: int) -> FeaturesOutSchema:
    try:
        return await crud.get_feature(id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Feature does not exist",
        )

@router.get(
    "/features",
    response_model=List[FeaturesOutSchema],
    dependencies=[Depends(get_current_user)],
)
async def get_features(
):
    print('get_features')
    try:
        return await crud.get_features()
    except:
        raise HTTPException(
            status_code=400,
            detail="Could not fetch features",
                )