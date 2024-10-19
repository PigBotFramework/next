from enum import Enum, unique


@unique
class OneBotVersion(Enum):
    v11 = "v11"
    v12 = "v12"


# Directories
user_directory = ".pbf"

# Database

# To use mysql database
# from peewee import MySQLDatabase
# sql_driver = MySQLDatabase(
#     "pbf",
#     host="localhost",
#     user="root",
#     password="password",
#     port=3306
# )

# To use sqlite database
from peewee import SqliteDatabase
from .utils import Path
sql_driver = SqliteDatabase(Path.replace("{home}/data.db"))

# Connect
ob_access_token = "access_token"
ob_uri = "http://localhost"
ob_version = OneBotVersion.v11  # or "v12"

# Plugins
plugins_directory = "{home}/plugins"
plugins_disabled = []
# Config for plugins
plugins_config = {}

# Logs
logs_directory = "{home}/logs"
logs_level = "DEBUG"
logs_format = "[%(asctime)s | %(levelname)s] %(message)s"
