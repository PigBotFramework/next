import pymysql
from . import SQL


def startup(
    host: str,
    user: str,
    password: str,
    database: str,
    port: int = 3306,
    charset: str = "utf8mb4"
):
    return SQL(pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        charset=charset
    ))