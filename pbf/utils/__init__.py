import pathlib
import os
import pip

from apscheduler.schedulers.background import BackgroundScheduler

# Debug
try:
    from ..config import user_directory
except ImportError:
    from pbf.config import user_directory

# Scheduler
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def installPackage(package: str):
        """
        Install package. (Blocked)
        :param package: str package name
        :return: None
        """
        pip.main(["install", package])


class Path:
    @staticmethod
    def make_sure_path_exists(path_to_file: str, replace: bool = True) -> None:
        """
        Make sure path exists.
        :param path_to_file: str path to file
        :param replace: bool (可选)是否替换path_to_file中的特殊路径
        :return: None
        """
        if replace:
            path_to_file = Path.replace(path_to_file)
        pathlib.Path(path_to_file).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def replace(path: str) -> str:
        """
        替换path中的特殊路径。
        :param path: str
        :return: str
        """
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
        """
        Initialize metadata.
        :param kwargs: **dict Metadata
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return f"{self.name} v{self.version} by {self.author}"

    def toDict(self):
        """
        Convert metadata to dict.
        :return: dict
        """
        ret_dict: dict = {}
        for i in dir(self):
            if not i.startswith("__") and not callable(getattr(self, i)):
                ret_dict[i] = getattr(self, i)
        return ret_dict
