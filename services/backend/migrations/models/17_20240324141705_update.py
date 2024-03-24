from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE bots
    ADD CONSTRAINT unique_groupme_league UNIQUE (groupme_bot_id, league_id, private);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE bots
        DROP CONSTRAINT IF EXISTS unique_groupme_league;
    """