from peewee import Model
from ..config import sql_driver


class BaseModel(Model):
    class Meta:
        database = sql_driver
