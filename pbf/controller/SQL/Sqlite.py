import sqlite3
from ...utils import Path
from . import SQL


def startup(file_path: str):
    file_path = Path.replace(file_path)
    return SQL(sqlite3.connect(file_path))
