from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ADD "discord_webhook_url" VARCHAR(200);
        ALTER TABLE "bots" ALTER COLUMN "groupme_bot_id" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" DROP COLUMN "discord_webhook_url";
        ALTER TABLE "bots" ALTER COLUMN "groupme_bot_id" SET NOT NULL;"""
