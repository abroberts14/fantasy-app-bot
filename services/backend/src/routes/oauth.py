import os
import base64
import requests
import time
from fastapi import APIRouter, Depends, HTTPException, Query
import cryptography.fernet as fernet
from src.database.models import OAuthTokens, Users
from src.schemas.users import UserOutSchema
from src.auth.jwthandler import get_current_user

from fastapi.responses import RedirectResponse

from tortoise.exceptions import DoesNotExist

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


@router.get("/oauth/yahoo/tokens")
async def get_oauth_tokens(current_user: UserOutSchema = Depends(get_current_user), user_id: int = Query()  # Optional query parameter
):
    try:
        #oauth_token = await OAuthTokens.get(user=current_user.id)
        oauth_token = await OAuthTokens.filter(user=current_user.id).first()
        # Serialize the OAuthTokens object
        token_data = {
            "id": oauth_token.id,
            "user_id": oauth_token.user_id,
            "provider": oauth_token.provider,
            # "access_token": oauth_token.access_token,
            # "refresh_token": oauth_token.refresh_token,
            "token_type": oauth_token.token_type,
            "expires_in": oauth_token.expires_in,
            "created_at": oauth_token.created_at,
            "modified_at": oauth_token.modified_at
        }
        return token_data
    except DoesNotExist:
        raise HTTPException(status_code=200, detail="OAuth token not found for the current user")

async def get_oauth_token_by_id(user_id: int):
    try:
        oauth_token = await OAuthTokens.filter(user=user_id).first()
        # Get the encryption key from the environment variable
        token_secret_key = os.getenv("TOKEN_SECRET_KEY")
        if not token_secret_key:
            raise HTTPException(status_code=500, detail="Encryption key not found")

        # Decrypt the access token
        f = fernet.Fernet(token_secret_key)
        decrypted_access_token = f.decrypt(oauth_token.access_token.encode()).decode()

        # Serialize the OAuthTokens object with decrypted access token
        token_data = {
            "id": oauth_token.id,
            "user_id": oauth_token.user_id,
            "provider": oauth_token.provider,
            "access_token": decrypted_access_token,
            "refresh_token": oauth_token.refresh_token,
            "token_type": oauth_token.token_type,
            "expires_in": oauth_token.expires_in,
            "created_at": oauth_token.created_at,
            "modified_at": oauth_token.modified_at
        }
        return token_data
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="OAuth token not found for the specified ID or not belonging to the current user")

@router.delete("/oauth/yahoo/tokens/{token_id}")
async def delete_oauth_token(token_id: int, current_user: UserOutSchema = Depends(get_current_user)):
    try:
        # Retrieve the token to ensure it exists and belongs to the current user
        oauth_token = await OAuthTokens.get(id=token_id, user_id=current_user.id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="OAuth token not found or does not belong to the current user")

    # Delete the token
    await oauth_token.delete()
    return {"detail": "OAuth token deleted successfully"}

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
        token_data = await exchange_code_for_token(code)
        if not token_data or 'access_token' not in token_data:
            print("No access token returned from exchange_code_for_token")
            return RedirectResponse(url=frontend_route + '/oauth-error')

        access_token = token_data['access_token']
        refresh_token = token_data.get('refresh_token')
        token_type = token_data.get('token_type')
        expires_in = token_data.get('expires_in')
        print('token type:', token_type)    
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