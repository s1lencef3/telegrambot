from peewee import *
from datetime import datetime
DB = SqliteDatabase('etusupportDB.sqlite')

types = ['source','task','lecture','checkpoint']

class BaseModel(Model):
    class Meta:
        database = DB


class User(BaseModel):
    id = IntegerField(primary_key=True)
    status = CharField()
    name = CharField()
    username = CharField()
    group = IntegerField()
    notifications = BooleanField(default=True)



class Item(BaseModel):
    id = IntegerField(primary_key=False)
    lesson = CharField(default='')
    value = CharField(default='')
    number = CharField(default=0)
    group = IntegerField(default=0000)
    kind = CharField(default='')
    date = DateTimeField(default= datetime.strptime('0001-1-1','%Y-%m-%d'))
    type = CharField()

class Group(BaseModel):
    number = IntegerField()
    password = CharField()

DB.create_tables([User,Item,Group])

