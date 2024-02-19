from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ADD "active" BOOL NOT NULL  DEFAULT True;
        ALTER TABLE "bots" ADD "running" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" DROP COLUMN "active";
        ALTER TABLE "bots" DROP COLUMN "running";"""
