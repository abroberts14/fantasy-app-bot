from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Bots
from src.schemas.bots import BotOutSchema
from src.schemas.token import Status


async def get_bots():
    return await BotOutSchema.from_queryset(Bots.all())


async def get_bot(bot_id) -> BotOutSchema:
    return await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))


async def create_bot(bot, current_user) -> BotOutSchema:
    bot_dict = bot.dict(exclude_unset=True)
    bot_dict["user_id"] = current_user.id
    bot_obj = await Bots.create(**bot_dict)
    return await BotOutSchema.from_tortoise_orm(bot_obj)


async def update_bot(bot_id, bot, current_user) -> BotOutSchema:
    try:
        db_bot = await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")

    if db_bot.user.id == current_user.id:
        await Bots.filter(id=bot_id).update(**bot.dict(exclude_unset=True))
        return await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))

    raise HTTPException(status_code=403, detail=f"Not authorized to update")


async def delete_bot(bot_id, current_user) -> Status:
    try:
        db_bot = await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")

    if db_bot.user.id == current_user.id:
        deleted_count = await Bots.filter(id=bot_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        return Status(message=f"Deleted Bot {bot_id}")

    raise HTTPException(status_code=403, detail=f"Not authorized to delete")
