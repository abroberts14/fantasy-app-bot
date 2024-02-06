from fastapi import FastAPI, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request

app = FastAPI()
oauth = OAuth(app)
{
    "consumer_key": "dj0yJmk9NTZlWXZjdlY1SUZhJmQ9WVdrOVkxWnZjemRJVVhFbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTgz",
    "consumer_secret": "e656aa67c44c49a1c201c4f984ef6b83fb09fe73"
  }
yahoo = oauth.register(
    name='yahoo',
    client_id='dj0yJmk9NTZlWXZjdlY1SUZhJmQ9WVdrOVkxWnZjemRJVVhFbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTgz',
    client_secret='e656aa67c44c49a1c201c4f984ef6b83fb09fe73',
    access_token_url='https://api.login.yahoo.com/oauth2/get_token',
    authorize_url='https://api.login.yahoo.com/oauth2/request_auth',
    api_base_url='https://api.login.yahoo.com/',
)

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await yahoo.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await yahoo.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = await yahoo.get('https://fantasysports.yahooapis.com/fantasy/v2/game/nfl', token=token)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get data from Yahoo API")

    return {"status_code": response.status_code, "response": response.text}