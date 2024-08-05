import pathlib
import os
from functools import wraps
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler

# Debug
try:
    from ..config import user_directory
except ImportError:
    from pbf.config import user_directory

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def print(*args, **kwargs):
        print("PBF Server:", *args, **kwargs)


class Scheduler:
    def __init__(self) -> None:
        pass


class Path:
    @staticmethod
    def make_sure_path_exists(path_to_file: str, replace: bool = True) -> None:
        if replace:
            path_to_file = Path.replace(path_to_file)
        pathlib.Path(path_to_file).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def replace(path: str) -> str:
        replace_list = {
            "home": os.path.join(pathlib.Path().home(), user_directory),
            "cwd": pathlib.Path().cwd(),
        }
        return path.format(**replace_list)


class MetaData:
    name: str = "PBFPlugin"
    version: str = "1.0.0"
    description: str = "PBF Plugin"
    author: str = "you"
    license: str = "MIT"
    keywords: list = ["pbf", "plugin"]
    readme: str = """
    # PBF Plugin
    hi
    """

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"{self.name} v{self.version} by {self.author}"


class PBFPlugin:
    def __init__(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class RegCmd:
    name: str = 'Command name'
    description: str = 'Command description'
    permission: str = 'cmd.permission.cmdname'
    usage: str = 'Command usage'
    alias: List[str] = []
    hidden: bool = False
    enabled: bool = True
    type: str = 'command'
    mode: str = '机器人操作'

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper


if __name__ == "__main__":
    testpath = Path.replace('{home}/test')
    Utils.print(testpath)
