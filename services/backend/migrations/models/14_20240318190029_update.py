from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ADD "timezone" VARCHAR(50) NOT NULL  DEFAULT 'America/New_York';
        ALTER TABLE "bots" DROP COLUMN "running";
        ALTER TABLE "bots" DROP COLUMN "active";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ADD "running" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "bots" ADD "active" BOOL NOT NULL  DEFAULT True;
        ALTER TABLE "bots" DROP COLUMN "timezone";"""
