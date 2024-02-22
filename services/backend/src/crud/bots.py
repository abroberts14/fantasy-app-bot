from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Bots, Apps
from src.schemas.bots import BotOutSchema
from src.schemas.token import Status
from src.crud.apps import update_all_apps, delete_entire_app

async def get_bots(user_id: int = None):
    try:
        await update_all_apps()
    except Exception as e:
        print(e)
    finally:
        if user_id:
            # Fetch bots for a specific user
            return await BotOutSchema.from_queryset(Bots.filter(user_id=user_id))
        else:
            # Fetch all bots (for admins in the future)
            return await BotOutSchema.from_queryset(Bots.all())
    
async def get_bot(bot_id) -> BotOutSchema:
    try:
        await update_all_apps()
    except Exception as e:
        print(e)
    finally:
    # try:
    #     bot = await Bots.get(id=bot_id)
    #     await bot.fetch_related('apps')  # Fetch the 'apps' field

    #     if bot and bot.apps:
    #         for app in bot.apps:  # Iterate over 'apps'
    #             if app.name:  # Access the 'id' of each app
    #                 s = await update_one_app(app.name)
    #                 print(s)
    # except Exception as e:
    #     print(e)
    # finally:
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
    print(f"Starting deletion of bot {bot_id} for user {current_user.id}")

    # Check if the bot exists and the current user is authorized to delete it
    try:
        db_bot = await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting bot {bot_id}: {str(e)}")
    if db_bot.user.id != current_user.id and current_user.role != "admin":
        print(f"User {current_user.id} is not authorized to delete bot {bot_id}")
        raise HTTPException(status_code=403, detail=f"Not authorized to delete")

    # If the bot has an associated app, delete the app
    if db_bot.app and db_bot.app.name:        
        print(f"Deleting associated app for bot {bot_id}")
        await delete_entire_app(db_bot.app.name)

    # Delete the bot (if it hasn't already been deleted by cascading delete)
    deleted_bot_count = await Bots.filter(id=bot_id).delete()
    if not deleted_bot_count:
        print(f"Bot {bot_id} was already deleted due to cascading delete")
    else:
        print(f"Successfully deleted bot {bot_id}")

    return Status(message=f"Deleted Bot {bot_id}")