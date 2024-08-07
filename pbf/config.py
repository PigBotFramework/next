# Version
version = "5.0.0"
version_code = 500
version_name = "5.0.0"

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
access_token = None

# Plugins
plugins_directory = "{home}/plugins"
plugins_disabled = []

# Logs
logs_directory = "{home}/logs"
logs_level = "DEBUG"
logs_format = "[%(asctime)s | %(levelname)s] %(message)s"
