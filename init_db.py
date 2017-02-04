from db import database
from models import SentinelScene

# Create table in a database

database.connect()
database.create_tables([SentinelScene])
