from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "apps" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'stopped',
    "running" BOOL NOT NULL  DEFAULT False,
    "paused" BOOL NOT NULL  DEFAULT False,
    "restarting" BOOL NOT NULL  DEFAULT False,
    "oom_killed" BOOL NOT NULL  DEFAULT False,
    "dead" BOOL NOT NULL  DEFAULT False,
    "pid" INT,
    "exit_code" INT NOT NULL  DEFAULT 0,
    "error" VARCHAR(255),
    "started_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "finished_at" TIMESTAMPTZ
);;
        ALTER TABLE "bots" ADD "app_id" INT;
        ALTER TABLE "bots" ADD CONSTRAINT "fk_bots_apps_d3c9d57d" FOREIGN KEY ("app_id") REFERENCES "apps" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bots" DROP CONSTRAINT "fk_bots_apps_d3c9d57d";
        ALTER TABLE "bots" DROP COLUMN "app_id";
        DROP TABLE IF EXISTS "apps";"""
