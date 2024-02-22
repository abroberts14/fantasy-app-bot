from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ALTER COLUMN "name" TYPE VARCHAR(20) USING "name"::VARCHAR(20);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);"""
