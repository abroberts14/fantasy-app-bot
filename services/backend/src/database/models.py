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
    oauth_tokens = fields.ReverseRelation["OAuthTokens"]  # Reverse relation for oauth_tokens
    
class OAuthTokens(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.Users', related_name='oauth_tokens')
    provider = fields.CharField(max_length=50)  # e.g., 'yahoo', 'google', etc.
    access_token = fields.TextField()  #   
    refresh_token = fields.TextField(null=True)
    token_type = fields.CharField(max_length=50)
    expires_in = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    class Meta:
        unique_together = ("provider", "user")

class Bots(models.Model):
    name = fields.CharField(max_length=20, null=True)
    league_id = fields.CharField(max_length=6)
    groupme_bot_id = fields.CharField(max_length=100,  null=True)
    discord_webhook_url = fields.CharField(max_length=200, null=True)
    user = fields.ForeignKeyField("models.Users", related_name="bots")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    timezone = fields.CharField(max_length=50, default="America/New_York")
    app = fields.ForeignKeyField("models.Apps", related_name="bots", null=True)
    features =  fields.ReverseRelation["features"]  # Reverse relation for bots
    private = fields.BooleanField(default=False)

    class Meta:
        unique_together = ("league_id", "groupme_bot_id")

    def __str__(self):
        return f"{self.name}, {self.groupme_bot_id} for league {self.league_id} - created on {self.created_at}"

    

class Features(models.Model):
    id = fields.IntField(pk=True)
    bot = fields.ForeignKeyField("models.Bots", related_name="features")
    global_feature = fields.ForeignKeyField("models.GlobalFeatures", related_name="global_features")
    # name = fields.CharField(max_length=50, unique=True)
    # hour = fields.IntField(min_value=0, max_value=23)
    # minute = fields.IntField(min_value=0, max_value=59)
    # description = fields.TextField(null=True, blank=True)  # Allow NULL and empty string
    enabled = fields.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class GlobalFeatures(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    day = fields.CharField(max_length=40, default="mon")
    hour = fields.IntField(min_value=0, max_value=23)
    minute = fields.IntField(min_value=0, max_value=59)
    live = fields.BooleanField(default=False)
    description = fields.TextField(null=True, blank=True)  # Allow NULL and empty strings
    def __str__(self):
        return self.name
    

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

