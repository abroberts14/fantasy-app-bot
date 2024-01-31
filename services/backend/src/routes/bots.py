from typing import List

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

import src.crud.bots as crud
from src.auth.jwthandler import get_current_user
from src.schemas.bots import BotOutSchema, BotInSchema, UpdateBot
from src.schemas.token import Status
from src.schemas.users import UserOutSchema


router = APIRouter()


@router.get(
    "/bots",
    response_model=List[BotOutSchema],
    dependencies=[Depends(get_current_user)],
)
async def get_bots():
    return await crud.get_bots()


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


@router.post(
    "/register-bot", response_model=BotOutSchema, dependencies=[Depends(get_current_user)]
)
async def create_bot(
    bot: BotInSchema, current_user: UserOutSchema = Depends(get_current_user)
) -> BotOutSchema:
    return await crud.create_bot(bot, current_user)


@router.patch(
    "/bot/{id}",
    dependencies=[Depends(get_current_user)],
    response_model=BotOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_bot(
    id: int,
    bot: UpdateBot,
    current_user: UserOutSchema = Depends(get_current_user),
) -> BotOutSchema:
    return await crud.update_bot(id, bot, current_user)


@router.delete(
    "/bot/{id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(get_current_user)],
)
async def delete_bot(
    id: int, current_user: UserOutSchema = Depends(get_current_user)
):
    return await crud.delete_bot(id, current_user)
