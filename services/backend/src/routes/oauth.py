import os
import base64
import requests
import time
from fastapi import APIRouter, Depends, HTTPException, status
import cryptography.fernet as fernet
from src.database.models import OAuthTokens, Users
from src.schemas.users import UserOutSchema
from src.auth.jwthandler import get_current_user

from fastapi.responses import RedirectResponse


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

@router.get("/oauth/yahoo/callback")
async def handle_oauth_callback(code: str = None, error: str = None, current_user: UserOutSchema = Depends(get_current_user)):
    frontend_route = os.getenv("FRONTEND_URL")    
    token_secret_key = os.getenv("TOKEN_SECRET_KEY")
    print('code:', code)
    if error:
        return RedirectResponse(url=frontend_route +'/oauth-error')

    if not code:
        return RedirectResponse(url=frontend_route +'/oauth-error')

    try:
        # Exchange the authorization code for an access token
        access_token, refresh_token, token_type, expires_in, token_time = await exchange_code_for_token(code)
        print(token_time)
        # Encrypt the token
        f = fernet.Fernet(token_secret_key)
        encrypted_access_token = f.encrypt(access_token.encode()).decode()
        user_instance = await Users.get(id=current_user.id)

        oauth_token = OAuthTokens(
            user=user_instance,  # Use the current user's ID
            provider="yahoo",
            access_token=encrypted_access_token,
            refresh_token=refresh_token,  # Assuming refresh_token is available
            token_type=token_type,
            expires_in=expires_in
        )

        await oauth_token.save()
        # Redirection after successful token handling
        return RedirectResponse(url=frontend_route + '/oauth-success')
    except Exception as e:
        # Log the error
        print(f"Error in handle_oauth_callback: {e}")
        return RedirectResponse(url=frontend_route + '/oauth-error')
    
@router.get("/oauth/yahoo/callback/test")
async def handle_oauth_callback(current_user: UserOutSchema = Depends(get_current_user)):
    frontend_route = os.getenv("FRONTEND_URL")    
    token_secret_key = os.getenv("TOKEN_SECRET_KEY")
    print('code:', token_secret_key)
  
    try:
        # Exchange the authorization code for an access token
        #access_token, refresh_token, token_type, expires_in = await exchange_code_for_token(code)

        test_token = {'access_token': 'test', 'refresh_token': 'test', 'expires_in': 3600, 'token_type': 'bearer', 'token_time': 1709321886.3136978}
        access_token = test_token['access_token']
        refresh_token = test_token['refresh_token']
        token_type = test_token['token_type']
        expires_in = test_token['expires_in']

        # Encrypt the token
        f = fernet.Fernet(token_secret_key)
        encrypted_access_token = f.encrypt(access_token.encode()).decode()
        user_instance = await Users.get(id=current_user.id)

        oauth_token = OAuthTokens(
            user=user_instance,  # Use the current user's ID
            provider="yahoo",
            access_token=encrypted_access_token,
            refresh_token=refresh_token,  # Assuming refresh_token is available
            token_type=token_type,
            expires_in=expires_in
        )

        await oauth_token.save()

        # Redirection after successful token handling
        return {"test": "success"}
    except Exception as e:
        # Log the error
        print(f"Error in handle_oauth_callback: {e}")
        return {"test": "error in handle_oauth_callback function " + str(e)}