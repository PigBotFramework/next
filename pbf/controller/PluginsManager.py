import os

try:
    from ..config import plugins_directory, plugins_disabled
    from ..utils.Logging import Logger
    from ..utils import Path
    from .. import ListenerManager
except ImportError:
    from pbf.config import plugins_directory, plugins_disabled
    from pbf.utils.Logging import Logger
    from pbf.utils import Path
    from pbf import ListenerManager

logger = Logger(__name__)


class PluginsManager:
    plugins: dict = {}
    plugin_name: str = None

    def __init__(self, path: str = plugins_directory):
        """
        :param path: Plugins directory path
        :return: None
        """
        self.path = Path.replace(path)

    def load_plugins(self):
        """
        :return: None
        """
        for plugin in os.listdir(self.path):
            logger.info(f"Loading plugin: `{plugin}`")
            if plugin in plugins_disabled:
                logger.warning(f"Plugin `{plugin}` is disabled")
                continue
            try:
                self.plugin_name = plugin
                plugin_distance = __import__(f"{plugin}")
                logger.info(plugin_distance.meta_data)
                with plugin_distance.Controller():
                    pass
                self.plugins[plugin] = plugin_distance
                logger.info(f"Plugin `{plugin}` loaded")
            except ImportError as e:
                logger.error(f"Plugin `{plugin}` failed to load: {e}")
            except Exception as e:
                logger.error(f"Plugin `{plugin}` failed to load: {e}")

    def disable(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: None
        """
        if plugin in self.plugins:
            self.plugins.pop(plugin)
            ListenerManager.remove_listener_by_plugin_name(plugin)
            logger.info(f"Plugin `{plugin}` disabled")
        else:
            logger.warning(f"Plugin `{plugin}` not found")

    def enable(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: None
        """
        try:
            plugin_distance = __import__(f"{plugin}")
            with plugin_distance.Controller():
                pass
            self.plugins[plugin] = plugin_distance
            logger.info(f"Plugin `{plugin}` enabled")
        except ImportError:
            logger.error(f"Plugin `{plugin}` failed to enable")
        except Exception as e:
            logger.error(f"Plugin `{plugin}` failed to enable: {e}")


if __name__ == "__main__":
    PluginsManager()
