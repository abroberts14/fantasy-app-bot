from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "globalfeatures" ADD "day" VARCHAR(3) NOT NULL  DEFAULT 'mon';
        ALTER TABLE "globalfeatures" ADD "live" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "globalfeatures" DROP COLUMN "day";
        ALTER TABLE "globalfeatures" DROP COLUMN "live";"""
