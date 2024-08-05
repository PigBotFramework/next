import sys
from .config import *
from .utils import Path

Path.make_sure_path_exists(logs_directory, replace=True)
Path.make_sure_path_exists(plugins_directory, replace=True)
sys.path.append(Path.replace(plugins_directory))
