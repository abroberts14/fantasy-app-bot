import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from src.database.models import Users
from src.schemas.token import TokenData
from src.schemas.users import UserOutSchema
from tortoise.exceptions import DoesNotExist, NoValuesFetched

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param


security = OAuth2PasswordBearerCookie(token_url="/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    try:
        # user_query = Users.get(username=token_data.username)
        # print(user_query)
        # user_query.oauth_present = bool(
        #     user_query.oauth_tokens
        # )  # True if tokens list is not empty
        # await user_query.save()

        # user = await UserOutSchema.from_queryset_single(
        #     Users.get(username=token_data.username)
        # )
        # Fetch user from the database
        user_query = await Users.get(username=token_data.username).prefetch_related(
            "oauth_tokens"
        )
        # user_query = await Users.get(username=token_data.username)
        print(f"User fetched: {user_query}")

        # Update oauth_present based on oauth_tokens
        user_query.oauth_present = bool(user_query.oauth_tokens)
        await user_query.save()
        print("User oauth_present status updated")

        # Create a user output schema from the updated user query
        user_output = await UserOutSchema.from_tortoise_orm(user_query)
        print(f"User output schema generated: {user_output}")
        # del user_output.oauth_tokens
        user_output.oauth_tokens = []

        return user_output
    except DoesNotExist:
        raise credentials_exception
    except NoValuesFetched as e:
        raise ValueError(
            f"Required data not fetched: {e}"
        )  # To handle and identify missing prefetch.
