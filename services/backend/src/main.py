from fastapi import FastAPI, APIRouter  
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from src.database.register import register_tortoise
from src.database.config import TORTOISE_ORM


# enable schemas to read relationship between models
Tortoise.init_models(["src.database.models"], "models")

"""
import 'from src.routes import users, must be after 'Tortoise.init_models'
why?
https://stackoverflow.com/questions/65531387/tortoise-orm-for-python-no-returns-relations-of-entities-pyndantic-fastapi
"""
from src.routes import users, bots

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:5173", "http://0.0.0.0:5000", "http://localhost:5000", "https://default-alb-1236013653.us-east-1.elb.amazonaws.com", "https://dolphin-app-n3ezl.ondigitalocean.app", "https://draftwarroom.com"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
api_router_v1 = APIRouter()
api_router_v1.include_router(users.router)
api_router_v1.include_router(bots.router)
app.include_router(api_router_v1)


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)


@app.get("/")
def home():
    return "Hello, World!"

@app.get('/api/health-check/')
async def health_check():
    return {"status": "OK"}
