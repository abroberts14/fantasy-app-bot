from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from tortoise.contrib.fastapi import HTTPNotFoundError

import src.crud.users as crud
from src.auth.users import validate_user
from src.schemas.token import Status
from src.schemas.users import UserInSchema, UserOutSchema
import os
import base64
import requests
import time
from src.auth.jwthandler import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter()

YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/"
YAHOO_AUTH_URI = "request_auth?redirect_uri=oob&response_type=code&client_id="



async def exchange_code_for_token(code):
    keys = {
        "consumer_key": os.getenv('YAHOO_CLIENT_ID'),
        "consumer_secret": os.getenv('YAHOO_CLIENT_SECRET')
    }
    encoded_creds = base64.b64encode(
        ("{0}:{1}".format(keys['consumer_key'], keys['consumer_secret'])).encode(
            "utf-8"
        )
    )
    details = requests.post(
        url="{}get_token".format(YAHOO_API_URL),
        data={
            "code": code,
            "redirect_uri": "oob",
            "grant_type": "authorization_code",
        },
        headers={
            "Authorization": "Basic {0}".format(encoded_creds.decode("utf-8")),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    ).json()

    details["token_time"] = time.time()
    return details

@router.get("/callback")
async def handle_oauth_callback(code: str = None, error: str = None):
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code")

    try:
        # Exchange the authorization code for an access token
        access_token = await exchange_code_for_token(code)

        # Here, use the user details to either create a new user or update an existing user
        # and then create a JWT token for the user
        # user = crud.your_user_handling_logic(user_details)
        # token = create_access_token(data={"sub": user.username})

        # Return the JWT token and user details
        print(access_token)
        return access_token
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/register", response_model=UserOutSchema)
async def create_user(user: UserInSchema) -> UserOutSchema:
    return await crud.create_user(user)


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends()):

    user = await validate_user(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    token = jsonable_encoder(access_token)
    content = {"message": "You've successfully logged in. Welcome back!"}
    response = JSONResponse(content=content)
    is_local = os.getenv('IS_LOCAL', 'false').lower() == 'true'
    print('is local: ', is_local)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="Lax" if is_local else "None",
        secure=not is_local,
        domain=".draftwarroom.com" if not is_local else "192.168.1.170"
        #domain=".draftwarroom.com" if not is_local else "localhost"

    )

    return response

@router.post("/logout")
async def logout():
    print('logging out')
    is_local = os.getenv('IS_LOCAL', 'false').lower() == 'true'
    content = {"message": "You've successfully logged out."}

    response = JSONResponse(content=content)
    response.set_cookie(
        "Authorization",
        value="",
        httponly=True,
        max_age=0,
        expires=0,
        samesite="Lax" if is_local else "None",
        secure=not is_local,
        domain=".draftwarroom.com" if not is_local else "localhost"
    )
    return response

@router.get(
    "/users/whoami", response_model=UserOutSchema, dependencies=[Depends(get_current_user)]
)
async def read_users_me(current_user: UserOutSchema = Depends(get_current_user)):
    return current_user


@router.delete(
    "/user/{user_id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(get_current_user)],
)
async def delete_user(
    user_id: int, current_user: UserOutSchema = Depends(get_current_user)
) -> Status:
    return await crud.delete_user(user_id, current_user)