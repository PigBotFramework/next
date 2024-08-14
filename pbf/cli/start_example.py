def content():
    # Step 1: import config and modify it
    from pbf import config

    config.logs_level = "DEBUG"
    # Modify more configurations here

    # Step 2: import setup and setup
    from pbf import setup

    setup.setup()

    # Step 3: import driver and start it
    if __name__ == "__main__":
        from pbf.driver import Fastapi

        Fastapi.start()
