import sys
from .config import *
from .utils import Path
from .controller.ListenerManager import ListenerManager
from .controller.PluginsManager import PluginsManager
from .utils.Logging import Logger
from .utils import scheduler
from .controller.Handler import Handler

Path.make_sure_path_exists(logs_directory, replace=True)
Path.make_sure_path_exists(plugins_directory, replace=True)
sys.path.append(Path.replace(plugins_directory))

logger = Logger(__name__)
pluginsManager = None

# **Important!!!**
# Must import logger, pluginsManager, ListenerManager from pbf.setup

def setup():
    """
    Initialize PBF. **Must be called before importing any driver.**
    :return: None
    """
    global pluginsManager
    pluginsManager = PluginsManager()
    pluginsManager.loadPlugins()

    scheduler.start()

class Debug:
    @staticmethod
    def commandRegister():
        from pbf.utils.Register import Command

        @Command(name="test", description="test command")
        def test_command():
            logger.debug("test command")

        logger.debug(str(ListenerManager.get_listeners_by_type("command")))
        logger.debug(ListenerManager.get_listeners_by_plugin_name("test"))
        func: Command = ListenerManager.get_listeners_by_plugin_name("test")[0]
        print(func.name)
        func.func()

    @staticmethod
    def pluginLoad():
        setup()

        handler = Handler("""
        {
            "id": "b6e65187-5ac0-489c-b431-53078e9d2bbb",
            "self": {
                "platform": "qq",
                "user_id": "123234"
            },
            "time": 1632847927.599013,
            "type": "message",
            "detail_type": "private",
            "sub_type": "",
            "message_id": "6283",
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": "test arg1"
                    }
                }
            ],
            "alt_message": "test arg1",
            "user_id": "sasdad",
            "qq.nickname": "海阔天空"
        }
        """)
        handler.handle()

    @staticmethod
    def statementTest():
        from .statement.AtStatement import AtStatement
        statement = AtStatement(2417481092)
        logger.debug(str(statement))

        from .utils.CQCode import CQCode
        cqcode = CQCode("[CQ:at,qq=2417481092]")
        logger.debug(str(cqcode.get("qq")))
        logger.debug(str(cqcode.toStatement()))

    @staticmethod
    def clientTest():
        from .controller.Client import Client
        client = Client()
        logger.debug(client.request("send_msg", {"group_id": 871260826, "message": "test"}))

        from .controller.Client import Msg
        from .controller.Data import Event
        from .statement.FaceStatement import FaceStatement
        msg = Msg("asfsdaf", FaceStatement(123), event=Event(**{"group_id": 871260826}))
        logger.debug(msg.send(image=False))
