# Step 1: import config and modify it
from pbf import config

config.logs_level = "DEBUG"
config.plugins_disabled = ["nsfw", "mcserver"]
config.plugins_config["webui"] = {
    "basic_auth": {
        "username": "admin",
        "password": "admin"
    }
}
config.plugins_config["mcserver"] = {
    "client_id": 123,
    "client_secret": 123,
    "qn": [871260826]
}
config.ob_uri = "http://localhost:1000"

from pbf.controller import Cache
Cache.set("test", "test")
Cache.set("owner_id", 123123123)

# Step 2: import setup and setup
from pbf import setup

setup.setup(__name__)

# Step 3: import driver and start it
if __name__ == "__main__":
    from pbf.driver import Fastapi

    Fastapi.start()
