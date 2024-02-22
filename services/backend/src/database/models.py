from tortoise import fields, models


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    password = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    bots = fields.ReverseRelation["bots"]  # Reverse relation for bots
    role = fields.CharField(max_length=20, default="user")
    
class Bots(models.Model):
    name = fields.CharField(max_length=20, null=True)
    league_id = fields.CharField(max_length=6)
    groupme_bot_id = fields.CharField(max_length=100)
    user = fields.ForeignKeyField("models.Users", related_name="bots")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    running = fields.BooleanField(default=False)
    active = fields.BooleanField(default=True)
    app = fields.ForeignKeyField("models.Apps", related_name="bots", null=True)

    class Meta:
        unique_together = ("league_id", "groupme_bot_id")

    def __str__(self):
        return f"{self.name}, {self.groupme_bot_id} for league {self.league_id} - created on {self.created_at}"
    
class Apps(models.Model):
    name = fields.CharField(max_length=255, unique=True)
    status = fields.CharField(max_length=50, default="stopped")
    running = fields.BooleanField(default=False)
    paused = fields.BooleanField(default=False)
    restarting = fields.BooleanField(default=False)
    oom_killed = fields.BooleanField(default=False)
    dead = fields.BooleanField(default=False)
    pid = fields.IntField(null=True)
    exit_code = fields.IntField(default=0)
    error = fields.CharField(max_length=255, null=True)
    started_at = fields.DatetimeField(auto_now_add=True)
    finished_at = fields.DatetimeField(null=True)
    bot = fields.ReverseRelation["Bots"]
    def __str__(self):
        return f"{self.name} - {self.state_status}"
    

