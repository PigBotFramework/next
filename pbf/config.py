# Version
version = "5.0.0"
version_code = 500
version_name = "5.0.0"

# Directories
user_directory = ".pbf"

# Database

# To use mysql database
# from .controller.SQL.Mysql import startup
# sql_driver = startup(
#     host="localhost",
#     user="root",
#     password="your password",
#     database="pbf"
# )

# To use sqlite database
from .controller.SQL.Sqlite import startup
sql_driver = startup("{home}/data.db")

# Connect
access_token = None

# Plugins
plugins_directory = "{home}/plugins"
plugins_disabled = []

# Logs
logs_directory = "{home}/logs"
logs_level = "DEBUG"
logs_format = "[%(asctime)s | %(levelname)s] %(message)s"
