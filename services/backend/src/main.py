from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise import Tortoise
from starlette.exceptions import HTTPException 

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM


# enable schemas to read relationship between models
Tortoise.init_models(["src.database.models"], "models")

"""
import 'from src.routes import users, must be after 'Tortoise.init_models'
why?
https://stackoverflow.com/questions/65531387/tortoise-orm-for-python-no-returns-relations-of-entities-pyndantic-fastapi
"""
from src.routes import users, bots, apps, features, oauth

app = FastAPI()

#allowed_origins = ["http://localhost:5173", "http://0.0.0.0:5173", "http://0.0.0.0:5000", "http://localhost:5000", "https://dolphin-app-n3ezl.ondigitalocean.app", "https://draftwarroom.com"],    
allowed_origins = [
    "http://localhost:5173",  # Local frontend development
    "http://localhost:5000",  # backend requests
    "https://dolphin-app-n3ezl.ondigitalocean.app",  # Production frontend
    "https://draftwarroom.com",  # Another production frontend
    "http://167.99.4.120:8000",
    "http://167.99.4.120"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,    
    allow_credentials=True,
    #allow_methods=["GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE"],
    allow_methods=["*"],
    #allow_headers=["Access-Control-Allow-Headers", 'Content-Type', 'Authorization', 'Access-Control-Allow-Origin', "Set-Cookie"],
    allow_headers=["*"],
)
api_router_v1 = APIRouter()
api_router_v1.include_router(users.router)
api_router_v1.include_router(bots.router)
api_router_v1.include_router(apps.router)
api_router_v1.include_router(features.router)
api_router_v1.include_router(oauth.router)

app.include_router(api_router_v1)

@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    print('non def exception handler')
    response = JSONResponse({"detail": str(exc.detail)}, status_code=exc.status_code)
    response.headers['Access-Control-Allow-Origin'] = str(request.headers.get('origin'))    
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # Add this line    
    return response

@app.exception_handler(Exception)
async def default_exception_handler(request: Request, exc: Exception):
    print('default exception handler')
    response = JSONResponse({"detail": "Internal Server Error"}, status_code=500)
    response.headers['Access-Control-Allow-Origin'] = str(request.headers.get('origin'))    
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # Add this line
    return response


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)


@app.get("/")
def home():
    return "Hello, World!"

@app.get('/api/health-check/')
async def health_check():
    return {"status": "OK"}
