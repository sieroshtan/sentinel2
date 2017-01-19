import peewee
from db import BaseModel


class SentinelScene(BaseModel):
    farm_id = peewee.IntegerField()
    scene = peewee.TextField()
    date = peewee.DateField()

    class Meta:
        db_table = 'sentinel_scenes'
