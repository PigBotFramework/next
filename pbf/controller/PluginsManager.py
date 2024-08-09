import os

try:
    from ..config import plugins_directory, plugins_disabled
    from ..utils.Logging import Logger
    from ..utils import Path, MetaData
    from .. import ListenerManager
except ImportError:
    from pbf.config import plugins_directory, plugins_disabled
    from pbf.utils.Logging import Logger
    from pbf.utils import Path, MetaData
    from pbf import ListenerManager

logger = Logger(__name__)


class PluginsManager:
    plugins: dict = {}
    api: dict = {}
    plugin_name: str = None

    def __init__(self, path: str = plugins_directory):
        """
        :param path: Plugins directory path
        :return: None
        """
        self.path = Path.replace(path)

    def loadPlugins(self):
        """
        :return: None
        """
        for plugin in os.listdir(self.path):
            logger.info(f"Loading plugin: `{plugin}`")
            if plugin in plugins_disabled:
                logger.warning(f"Plugin `{plugin}` is disabled")
                continue
            self.plugin_name = plugin
            self.loadPlugin(plugin)

    def has(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: bool
        """
        return plugin in self.plugins

    def hasApi(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: bool
        """
        return plugin in self.api

    def checkDependency(self, plugins: dict):
        """
        Plugins dependencies struct:
        {
            "plugin_name": {
                "upper": 1,
                "lower": 1
            }
        }
        :param plugins: Plugins dependencies
        :return: bool, str
        """
        for key, value in plugins:
            upper = value.get("upper")
            lower = value.get("lower")
            if self.plugins.get(key) is None:
                return False, f"Plugin `{key}` not found"
            meta_data: MetaData = self.plugins.get(key).meta_data
            if upper is not None:
                if meta_data.versionCode > upper:
                    return False, f"Plugin `{key}` version is too high"
            if lower is not None:
                if meta_data.versionCode < lower:
                    return False, f"Plugin `{key}` version is too low"
        return True, "All dependencies are met"

    def require(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: Object
        """
        if plugin in self.api:
            return self.api[plugin]
        raise Exception(f"Plugin `{plugin}` not found or has no API")

    def disable(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: None
        """
        if plugin in self.plugins:
            self.plugins.pop(plugin)
            self.api.pop(plugin)
            ListenerManager.remove_listener_by_plugin_name(plugin)
            logger.info(f"Plugin `{plugin}` disabled")
        else:
            logger.warning(f"Plugin `{plugin}` not found")

    def loadPlugin(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: None
        """
        try:
            plugin_distance = __import__(f"{plugin}")
            logger.info(plugin_distance.meta_data)
            try:
                plugin_distance._enter()
            except Exception:
                pass
            try:
                self.api[plugin] = plugin_distance.Api
            except Exception:
                pass
            self.plugins[plugin] = plugin_distance
            logger.info(f"Plugin `{plugin}` loaded")
        except ImportError as e:
            logger.error(f"Plugin `{plugin}` failed to load: {e}")
        except Exception as e:
            logger.error(f"Plugin `{plugin}` failed to load: {e}")

    def enable(self, plugin: str):
        """
        :param plugin: Plugin name
        :return: None
        """
        self.loadPlugin(plugin)

    def getAllPlugins(self):
        """
        :return: dict
        """
        ret_dict: dict = {}
        for key, value in self.plugins.items():
            ret_dict[key] = value.meta_data.toDict()
        return ret_dict


if __name__ == "__main__":
    PluginsManager()
