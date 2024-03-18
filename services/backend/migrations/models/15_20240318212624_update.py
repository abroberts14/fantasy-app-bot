from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "globalfeatures" ALTER COLUMN "day" TYPE VARCHAR(40) USING "day"::VARCHAR(40);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "globalfeatures" ALTER COLUMN "day" TYPE VARCHAR(3) USING "day"::VARCHAR(3);"""
