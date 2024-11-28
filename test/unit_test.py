import re
import json
import time

from pbf import config
config.logs_directory = "./logs"
config.logs_level = "DEBUG"
config.plugins_directory = "./plugins"
config.plugins_disabled = ["tplgin"]
from pbf.setup import logger, ListenerManager, setup
setup(__name__)

from pbf.controller.Handler import Handler
from pbf.controller.Client import Client, Msg
from pbf.controller.Data import Event
from pbf.statement.AtStatement import AtStatement
from pbf.statement.FaceStatement import FaceStatement
from pbf.utils.CQCode import CQCode
from pbf.utils.Register import Command, RegexMode, Limit


def ownerPermission(event):
    if event.sender.get("role", "member") == "owner":
        return True
    logger.debug("You are not the owner.")
    return False


v12_message_event = {
    "id": "b6e65187-5ac0-489c-b431-53078e9d2bbb",
    "self": {
        "platform": "qq",
        "user_id": "123234"
    },
    "sender": {
        "role": "owner",
        "user_id": "123test",
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
    "user_id": "123test",
    "qq.nickname": "海阔天空"
}


class Debug:
    @staticmethod
    def commandRegister():
        """
        基础指令注册测试。v5.0.0加入
        :return:
        """
        @Command(name="test", description="test command")
        def test_command(event: Event):
            logger.debug("test command")
            logger.debug("event: " + str(event))

        logger.debug(str(ListenerManager.get_listeners_by_type("command")))
        logger.debug(ListenerManager.get_listeners_by_plugin_name("test"))
        func: Command = ListenerManager.get_listeners_by_plugin_name("test")[0]
        print(func.name)
        func.func()

    @staticmethod
    def pluginLoad():
        """
        插件加载测试。v5.0.0加入
        :return:
        """
        # setup(__name__)
        setup("__mp_main__")

        handler = Handler(json.dumps(v12_message_event))
        handler.handle()

    @staticmethod
    def statementTest():
        """
        语句测试。v5.0.0加入
        :return:
        """
        statement = AtStatement(2417481092)
        logger.debug(str(statement))

        cqcode = CQCode("[CQ:at,qq=2417481092]")
        logger.debug(str(cqcode.get("qq")))
        logger.debug(str(cqcode.toStatement()))

    @staticmethod
    def clientTest():
        """
        客户端测试。v5.0.0加入
        :return:
        """
        client = Client()
        logger.debug(client.request("send_msg", {"group_id": 871260826, "message": "test"}))

        msg = Msg("123test", FaceStatement(123), event=Event(**{"group_id": 871260826}))
        logger.debug(msg.send(image=False))

    @staticmethod
    def cmdAliasAndRegex():
        """
        别名和正则表达式测试。v5.0.11加入
        :return:
        """
        # setup(__name__)
        @Command(
            name=r"(.*) are (.*?) .*",
            description="test command",
            alias=["asd", "wow"],
            regex_mode=RegexMode.match,  # 启用正则match模式
            regex_flags=re.I|re.M,
            permission=ownerPermission
        )
        def foo_command(event: Event, listener: Command, match: re.Match):  # 可接受[0, 3]个参数，按顺序为event, listener, match
            logger.debug("foo command")
            logger.debug("event: " + str(event))
            logger.debug("listener: " + str(listener))
            logger.debug("permission: " + str(listener.permission))
            logger.debug("match: " + str(match))
            logger.debug("match.group(): " + str(match.group()))
            logger.debug("match.group(1): " + str(match.group(1)))
            logger.debug("match.group(2): " + str(match.group(2)))

        v12_message_event["alt_message"] = input(">>> ")
        handler = Handler(json.dumps(v12_message_event))
        handler.handle()

    @staticmethod
    def limitedCommand():
        def callback(event, func):  # 限制回调函数
            logger.debug("You have exceeded the limit.")
            logger.debug("event: " + str(event))
            logger.debug("But I allow you to call the function.")
            func(event)

        @Command(
            name="test",
            description="wow",
            permission=ownerPermission
        )
        @Limit(duration=1, times=3, callback=callback)  # 注册限制，1秒内最多调用3次
        def test_command(_: Event):
            logger.debug("test command was called")

        v12_message_event["alt_message"] = "test"
        def test1():  # 测试同一个人连续触发指令
            handler = Handler(json.dumps(v12_message_event))
            for iter in range(30):
                handler.handle()
                if (iter+1) % 5 == 0:
                    time.sleep(2)

        def test2():  # 不同人触发指令
            for iter in range(10):
                v12_message_event["user_id"] = f"test{iter}"
                handler = Handler(json.dumps(v12_message_event))
                for _ in range(5):
                    handler.handle()

        def test3():  # 不同人连续触发指令
            for iter in range(30):
                v12_message_event["user_id"] = f"test{iter}"
                handler = Handler(json.dumps(v12_message_event))
                handler.handle()

        # test1()
        # test2()
        test3()

if __name__ == '__main__':
    Debug.limitedCommand()
