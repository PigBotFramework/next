import pathlib
import os
import pip

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

    @staticmethod
    def installPackage(package: str):
        pip.main(["install", package])


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
    versionCode: int = 1
    description: str = "PBF Plugin"
    author: str = "author"
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

    def toDict(self):
        ret_dict: dict = {}
        for i in dir(self):
            if not i.startswith("__") and not callable(getattr(self, i)):
                ret_dict[i] = getattr(self, i)
        return ret_dict


if __name__ == "__main__":
    testpath = Path.replace('{home}/test')
    Utils.print(testpath)
