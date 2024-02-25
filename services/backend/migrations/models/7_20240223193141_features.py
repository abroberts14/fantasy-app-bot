from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "features" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "hour" INT NOT NULL,
    "minute" INT NOT NULL
);;
        CREATE TABLE IF NOT EXISTS "botfeatures" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "enabled" BOOL NOT NULL  DEFAULT True,
    "bot_id" INT NOT NULL REFERENCES "bots" ("id") ON DELETE CASCADE,
    "feature_id" INT NOT NULL REFERENCES "features" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_botfeatures_bot_id_235b4c" UNIQUE ("bot_id", "feature_id")
);;"""

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "botfeatures";
        DROP TABLE IF EXISTS "features";"""
