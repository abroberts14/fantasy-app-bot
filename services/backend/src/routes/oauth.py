import os
import base64
import requests
import time
from fastapi import APIRouter, Depends, HTTPException, status, RedirectResponse



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
async def handle_oauth_callback(code: str = None, error: str = None):
    frontend_route = os.getenv("FRONTEND_URL")

    if error:
        return RedirectResponse(url=frontend_error_route +'/oauth-error')

    if not code:
        return RedirectResponse(url=frontend_error_route +'/oauth-error')
    try:
        # Exchange the authorization code for an access token
        access_token = await exchange_code_for_token(code)

        # Here, use the user details to either create a new user or update an existing user
        # and then create a JWT token for the user
        # user = crud.your_user_handling_logic(user_details)
        # token = create_access_token(data={"sub": user.username})

        # Return the JWT token and user details
        print(access_token)
        return RedirectResponse(url=frontend_route+'/oauth-success')
    except Exception as e:
        frontend_error_route = "https://yourfrontend.com/oauth-error"
        return RedirectResponse(url=frontend_error_route +'/oauth-error')
