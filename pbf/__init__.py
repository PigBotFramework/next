import sys
from .config import *
from .utils import Path
from .controller.ListenerManager import ListenerManager
from .controller.PluginsManager import PluginsManager
from .utils.Logging import Logger

Path.make_sure_path_exists(logs_directory, replace=True)
Path.make_sure_path_exists(plugins_directory, replace=True)
sys.path.append(Path.replace(plugins_directory))

logger = Logger(__name__)
pluginsManager = None


def start(driver):
    global pluginsManager
    pluginsManager = PluginsManager()
    pluginsManager.load_plugins()

    driver.run()


def debug():
    from pbf.utils.Register import Command

    @Command(name="test", description="test command")
    def test_command():
        logger.debug("test command")

    logger.debug(str(ListenerManager.get_listeners_by_type("command")))
    logger.debug(ListenerManager.get_listeners_by_plugin_name("test"))
    func: Command = ListenerManager.get_listeners_by_plugin_name("test")[0]
    print(func.name)
    func.func()
