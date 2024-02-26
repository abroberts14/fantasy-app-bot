from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    CREATE TABLE IF NOT EXISTS "globalfeatures" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "hour" INT NOT NULL,
    "minute" INT NOT NULL,
    "description" TEXT
);;
        CREATE TABLE IF NOT EXISTS "features" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "enabled" BOOL NOT NULL  DEFAULT True,
    "bot_id" INT NOT NULL REFERENCES "bots" ("id") ON DELETE CASCADE,
    "global_feature_id" INT NOT NULL REFERENCES "globalfeatures" ("id") ON DELETE CASCADE
);;
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "features";
        DROP TABLE IF EXISTS "globalfeatures";"""
