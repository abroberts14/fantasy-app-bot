from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Bots, Features
from src.schemas.bots import BotOutSchema, BotInSchema
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

async def update_bot_features(bot_id, bot_features) -> BotOutSchema:
    try:
        print(f"Fetching bot with ID {bot_id}")
        db_bot = await BotOutSchema.from_queryset_single(Bots.get(id=bot_id))
        print(f"Bot found: {db_bot}")
    except DoesNotExist:
        print(f"Bot {bot_id} not found")
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")

    bot_dict = db_bot.dict(exclude_unset=False)
    print(f"Bot data: {bot_dict}")

    bot_features_data = bot_dict.pop('features', [])
    print(f"Existing bot features: {bot_features_data}")

    for feature_in in bot_features:
        feature_data = feature_in.dict()
        print(f"Processing feature: {feature_data}")
        feature_id = feature_data.get('global_feature_id')
        enabled_status = feature_data.get('enabled')

        if feature_id is not None:
            print(f"Processing feature with ID {feature_id}")
            print(f"Feature data: {feature_data}")

            feature_obj, created = await Features.get_or_create(
                bot=bot_dict['id'],
                global_feature_id=feature_id,
                defaults={'enabled': enabled_status}
            )
            print("created feature")
            
            if not created:
                feature_obj.enabled = enabled_status
                await feature_obj.save()
                print(f"Feature updated with new enabled status: {feature_obj.enabled}")
        else:
            print(f"Feature ID not found in feature data: {feature_data}")
    return db_bot


async def create_bot(bot: BotInSchema, current_user) -> BotOutSchema:
    print("Starting bot creation process")

    bot_dict = bot.dict(exclude_unset=True)
    print(f"Bot data before processing: {bot_dict}")

    bot_features_data = bot_dict.pop('features', [])
    print(f"Bot features data: {bot_features_data}")

    bot_dict["user_id"] = current_user.id
    print(f"Adding current user ID {current_user.id} to bot data")

    bot_obj = await Bots.create(**bot_dict)
    print(f"Bot created: {bot_obj}")

    for feature_data in bot_features_data:
        feature_id = feature_data.get('global_feature_id')
        if feature_id:
            print(f"Processing feature with ID {feature_id}")
            feature_obj, created = await Features.get_or_create(
                bot=bot_obj,
                global_feature_id=feature_id,
                defaults={'enabled': feature_data['enabled']}
            )

            print('created feature')
            if not created:
                feature_obj.enabled = feature_data['enabled']
                await feature_obj.save()
                print(f"Feature updated with new enabled status: {feature_obj.enabled}")
    
    created_bot = await Bots.get(id=bot_obj.id)
    print(f"Final bot object fetched: {created_bot}")

    return await BotOutSchema.from_tortoise_orm(created_bot)


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