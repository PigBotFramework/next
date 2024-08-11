import os

try:
    from ..config import plugins_directory, plugins_disabled
    from ..utils.Logging import Logger
    from ..utils import Path, MetaData
    from ..setup import ListenerManager
except ImportError:
    from pbf.config import plugins_directory, plugins_disabled
    from pbf.utils.Logging import Logger
    from pbf.utils import Path, MetaData
    from pbf.setup import ListenerManager

logger = Logger(__name__)


class PluginsManager:
    plugins: dict = {}
    api: dict = {}
    plugin_name: str = None

    def __init__(self, path: str = plugins_directory):
        """
        初始化PluginsManager。
        :param path: str (可选)插件目录，默认为`pbf.config.plugins_directory`
        :return: None
        """
        self.path = Path.replace(path)

    def loadPlugins(self):
        """
        Load all plugins in the directory.
        :return: None
        """
        for plugin in os.listdir(self.path):
            if plugin.startswith("__"):
                continue
            if plugin.endswith(".py"):
                plugin = plugin[:-3]
            logger.info(f"Loading plugin: `{plugin}`")
            if plugin in plugins_disabled:
                logger.warning(f"Plugin `{plugin}` is disabled")
                continue
            self.plugin_name = plugin
            self.loadPlugin(plugin)

    def has(self, plugin: str):
        """
        Check if the plugin exists.
        :param plugin: str Plugin name
        :return: bool
        """
        return plugin in self.plugins

    def hasApi(self, plugin: str):
        """
        Check if the plugin has an API.
        :param plugin: str Plugin name
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
        :param plugins: dict Plugins dependencies
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
        Require the plugin API.
        :param plugin: str Plugin name
        :return: Api Object
        """
        if self.hasApi(plugin):
            return self.api[plugin]
        raise Exception(f"Plugin `{plugin}` not found or has no API")

    def disable(self, plugin: str):
        """
        Disable the plugin.
        :param plugin: str Plugin name
        :return: None
        """
        if self.has(plugin):
            self.plugins.pop(plugin)
            if self.hasApi(plugin):
                self.api.pop(plugin)
            ListenerManager.remove_listener_by_plugin_name(plugin)
            logger.info(f"Plugin `{plugin}` disabled")
        else:
            logger.warning(f"Plugin `{plugin}` not found")

    def loadPlugin(self, plugin: str):
        """
        Load the plugin.
        :param plugin: str Plugin name
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
        Enable the plugin.
        :param plugin: str Plugin name
        :return: None
        """
        self.loadPlugin(plugin)

    def getAllPlugins(self):
        """
        Get all plugins.
        :return: dict
        """
        ret_dict: dict = {}
        for key, value in self.plugins.items():
            ret_dict[key] = value.meta_data.toDict()
        return ret_dict


if __name__ == "__main__":
    PluginsManager()
