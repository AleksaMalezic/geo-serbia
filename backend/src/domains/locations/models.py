from tortoise import fields
from tortoise.models import Model

class Location(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    image_url = fields.CharField(max_length=200, null=True)
    hints = fields.JSONField(null=True)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    created_by = fields.ForeignKeyField("models.User", related_name="locations")
    is_approved = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "locations"

    def __str__(self):
        return self.name
