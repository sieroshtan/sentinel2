import peewee
from db import BaseModel


class SentinelScene(BaseModel):
    farm_id = peewee.IntegerField()
    scene = peewee.TextField()
    date = peewee.DateField()
    ndvi = peewee.DecimalField(max_digits=4, decimal_places=3)
    nmdi = peewee.DecimalField(max_digits=4, decimal_places=3)

    class Meta:
        db_table = 'sentinel_scenes'
