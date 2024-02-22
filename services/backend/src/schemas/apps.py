from tortoise.contrib.pydantic import pydantic_model_creator
from src.database.models import Apps

AppInSchema = pydantic_model_creator(
    Apps, 
    name="AppIn", 
    exclude=["user_id"],
    #include=["name", "running", "pid", "name"],
    #include=["bot_name", "template_id", "BOT_ID", "BOT_TYPE", "LEAGUE_ID"],
    exclude_readonly=True
)

AppOutSchema = pydantic_model_creator(
    Apps, 
    name="Application", 
    include=["status", "running", "pid", "name"]
)