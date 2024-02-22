from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist, IntegrityError

import src.crud.apps as crud
from src.auth.jwthandler import get_current_user
from src.schemas.apps import AppInSchema, AppOutSchema
from src.schemas.bots import BotInSchema, BotOutSchema
from src.schemas.users import UserOutSchema
from src.database.models import Bots, Apps

router = APIRouter()


@router.get(
    "/app/{app_id}",
    response_model=AppOutSchema,
    dependencies=[Depends(get_current_user)],
)
async def get_app(app_id: str,
):
    try:
        return await crud.get_app(app_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="App does not exist",
        )

@router.get(
    "/apps",
    response_model=List[AppOutSchema],
    dependencies=[Depends(get_current_user)],
)
async def get_apps(
    current_user: UserOutSchema = Depends(get_current_user),
    user_id: int = Query(None)  # Optional query parameter

):
    if current_user.role == "admin":
        crud.update_all_apps()
        return await AppOutSchema.from_queryset(Apps.all())
    else:
        raise HTTPException(
            status_code=403,
                )

# {"name": "backend",  "groupme_bot_id": "6b5dfa374f148c64eb1e9948f5", "league_id": "3932"}

@router.post(
    "/apps/start-app/{bot_id}", response_model=AppOutSchema, dependencies=[Depends(get_current_user)]
)
async def create_app(bot_id) -> AppOutSchema:
    try:
        print(bot_id)
        db_bot_instance = await Bots.get(id=bot_id)
        db_bot = await BotOutSchema.from_tortoise_orm(db_bot_instance)

        print (db_bot)
        return await crud.create_and_deploy_app(bot_id, db_bot)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"A bot with the provided details already exists. Error: {str(e)}"
        )