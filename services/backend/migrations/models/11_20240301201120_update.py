from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_oauthtokens_provide_f611dc" ON "oauthtokens" ("provider", "user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "uid_oauthtokens_provide_f611dc";"""
