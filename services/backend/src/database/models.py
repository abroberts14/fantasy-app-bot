from tortoise import fields, models


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    password = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    notes = fields.ReverseRelation["notes"]  # Reverse relation for notes
    bots = fields.ReverseRelation["bots"]  # Reverse relation for bots

class Notes(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=225)
    content = fields.TextField()
    user = fields.ForeignKeyField("models.Users", related_name="notes")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}, {self.user_id} on {self.created_at}"


class Bots(models.Model):
    name = fields.CharField(max_length=50, null=True)
    league_id = fields.CharField(max_length=6)
    groupme_bot_id = fields.CharField(max_length=100)
    user = fields.ForeignKeyField("models.Users", related_name="bots")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = ("league_id", "groupme_bot_id")

    def __str__(self):
        return f"{self.name}, {self.groupme_bot_id} for league {self.league_id} - created on {self.created_at}"