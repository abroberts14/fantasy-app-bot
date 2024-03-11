from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist, IntegrityError

import src.crud.bots as crud
import src.crud.apps as app_crud
from src.auth.jwthandler import get_current_user
from src.schemas.bots import BotOutSchema, BotInSchema, UpdateBot, FeaturesInSchema
from src.schemas.token import Status
from src.schemas.users import UserOutSchema


router = APIRouter()


@router.get(
    "/bot/{id}",
    response_model=BotOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def get_bot(id: int) -> BotOutSchema:
    try:
        return await crud.get_bot(id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Bot does not exist",
        )



@router.get(
    "/bots",
    response_model=List[BotOutSchema],
    dependencies=[Depends(get_current_user)],
)
async def get_bots(
    current_user: UserOutSchema = Depends(get_current_user),
    user_id: int = Query(None)  # Optional query parameter
):
    if user_id is not None:
    # Admin requesting specific user's bots
        return await crud.get_bots(user_id)
    else:
        if current_user.role == "admin":
            return await crud.get_bots()
        else:
            raise HTTPException(
                status_code=403,
                    )
    

@router.post(
    "/register-bot", response_model=BotOutSchema, dependencies=[Depends(get_current_user)]
)
async def create_bot(
    bot: BotInSchema, current_user: UserOutSchema = Depends(get_current_user)
) -> BotOutSchema:
    if not bot.groupme_bot_id and not bot.discord_webhook_url:
        raise HTTPException(
            status_code=400,
            detail="Either 'groupme_bot_id' or 'discord_webhook_url' must be provided."
     )

    try:
        return await crud.create_bot(bot, current_user)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"A bot with the provided details already exists. Error details: {str(e)}"
        )

@router.patch(
    "/bot/{id}",
    dependencies=[Depends(get_current_user)],
    response_model=BotOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_bot(
    id: int,
    features: List[FeaturesInSchema],
    current_user: UserOutSchema = Depends(get_current_user),
) -> BotOutSchema:
    
    updated_bot = await crud.update_bot_features(id, features)
    return updated_bot

@router.delete(
    "/bot/{id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(get_current_user)],
)
async def delete_bot(
    id: int, current_user: UserOutSchema = Depends(get_current_user)
):
    print('ROUTE TO DELETE BOT: ' + str(id))
    return await crud.delete_bot(id, current_user)
