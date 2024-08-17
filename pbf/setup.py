import sys
from . import config
from .utils import Path


Path.make_sure_path_exists(config.logs_directory, replace=True)
Path.make_sure_path_exists(config.plugins_directory, replace=True)
sys.path.append(Path.replace(config.plugins_directory))


from .controller.ListenerManager import ListenerManager
from .controller.PluginsManager import PluginsManager
from .utils.Logging import Logger
from .utils import scheduler


logger = Logger(__name__)
pluginsManager = None


# **Important!!!**
# Must import logger, pluginsManager, ListenerManager from pbf.setup

def setup(_name):
    """
    Initialize PBF. **Must be called before importing any driver.**
    :return: None
    """
    logger.debug(f"Setup __name__: {_name}")
    flag: bool = True if _name == "__mp_main__" else False

    global pluginsManager
    pluginsManager = PluginsManager()
    pluginsManager.loadPlugins(enter=flag)

    logger.debug(f"ListenerManager is ready: {ListenerManager}")

    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Error in starting scheduler: {e}")
