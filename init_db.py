from db import database
from models import SentinelScene

database.connect()
database.create_tables([SentinelScene])
