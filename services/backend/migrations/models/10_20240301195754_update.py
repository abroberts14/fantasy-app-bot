from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE TEXT USING "access_token"::TEXT;
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE TEXT USING "access_token"::TEXT;
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE TEXT USING "access_token"::TEXT;
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE TEXT USING "refresh_token"::TEXT;
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE TEXT USING "refresh_token"::TEXT;
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE TEXT USING "refresh_token"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE VARCHAR(255) USING "access_token"::VARCHAR(255);
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE VARCHAR(255) USING "access_token"::VARCHAR(255);
        ALTER TABLE "oauthtokens" ALTER COLUMN "access_token" TYPE VARCHAR(255) USING "access_token"::VARCHAR(255);
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE VARCHAR(255) USING "refresh_token"::VARCHAR(255);
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE VARCHAR(255) USING "refresh_token"::VARCHAR(255);
        ALTER TABLE "oauthtokens" ALTER COLUMN "refresh_token" TYPE VARCHAR(255) USING "refresh_token"::VARCHAR(255);"""
