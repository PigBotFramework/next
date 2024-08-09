import pbf

pbf.config.logs_level = "DEBUG"

pbf.start()

if __name__ == "__main__":
    from pbf.driver import Fastapi
    Fastapi.start()