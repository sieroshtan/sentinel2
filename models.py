import peewee
from db import BaseModel


class SentinelScene(BaseModel):
    scene = peewee.TextField()
    datetime = peewee.DateField()

    class Meta:
        db_table = 'sentinel_scenes'
