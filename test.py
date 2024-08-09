import pbf

pbf.config.logs_level = "DEBUG"
# modify more config here

pbf.start()

if __name__ == "__main__":
    from pbf.driver import Fastapi
    Fastapi.start()
