from src.database.models import Users
from tortoise.contrib.pydantic import pydantic_model_creator

UserInSchema = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)
UserOutSchema = pydantic_model_creator(
    Users,
    name="UserOut",
    exclude=["password", "created_at", "modified_at", "players"],
)

# Other schemas remain unchanged
UserDatabaseSchema = pydantic_model_creator(
    Users, name="User", exclude=["created_at", "modified_at"]
)
