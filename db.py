import peewee


database = peewee.PostgresqlDatabase(
    'solum',
    user='agvestouser',
    password='agvestowater78',
    host='agvestodbinstance.cbld6msyrncu.eu-west-1.rds.amazonaws.com',
    port=5432
)


class BaseModel(peewee.Model):
    id = peewee.PrimaryKeyField()

    class Meta:
        database = database
