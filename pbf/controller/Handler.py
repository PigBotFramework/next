import json
import re
import inspect
from typing import Union, Tuple

from .Data import Event
from ..utils.Logging import Logger
from ..setup import ListenerManager
from ..utils.Register import Base as RegisterBase
from ..utils.Register import RegexMode

logger = Logger(__name__)


class Handler:
    def __init__(self, event_data: str) -> None:
        """
        Initialize the Handler.
        :param event_data: str 事件数据
        """
        self.data = json.loads(event_data)
        self.event: Event = Event()
        self.classify()
        logger.info(f"{self.event.sender.get('nickname', '未知昵称')}({self.event.user_id}): {self.event.raw_message}")

    def classify(self) -> Event:
        """
        统一OBv11和OBv12数据格式。
        :return: Event
        """
        if "self" in self.data:
            self.data["self_id"] = self.data["self"].get("user_id")
            del self.data["self"]

        if "post_type" in self.data:
            self.data["type"] = self.data["post_type"]
            del self.data["post_type"]

        if "message_type" in self.data:
            self.data["detail_type"] = self.data["message_type"]
            del self.data["message_type"]

        if "notice_type" in self.data:
            self.data["detail_type"] = self.data["notice_type"]
            del self.data["notice_type"]

        if "request_type" in self.data:
            self.data["detail_type"] = self.data["request_type"]
            del self.data["request_type"]

        if "meta_event_type" in self.data:
            self.data["detail_type"] = self.data["meta_event_type"]
            del self.data["meta_event_type"]

        if "alt_message" in self.data:
            self.data["raw_message"] = self.data["alt_message"]
            del self.data["alt_message"]

        if "qq.nickname" in self.data:
            self.data["sender"] = {
                "user_id": self.data["user_id"],
                "nickname": self.data["qq.nickname"]
            }
            del self.data["qq.nickname"]

        if "sender" not in self.data:
            self.data["sender"] = {
                "user_id": self.data.get("user_id")
            }

        if "raw_message" in self.data:
            self.data["message_list"] = self.data["raw_message"].split()

        event = Event(**self.data)
        self.event = event
        return event

    def handle(self) -> bool:
        """
        Handle the event.
        :return: bool
        """
        listeners = ListenerManager.get_listeners_by_type(self.event.type)
        for _, value in listeners.items():
            for listener in value:
                if listener.permission(self.event):
                    listener.func(self.event)

        def matchCommand(listener: RegisterBase) -> Tuple[bool, Union[None, re.Match]]:
            raw_message = self.event.raw_message
            # 如果 regex_mode 是 none，直接匹配前缀
            if listener.regex_mode == RegexMode.none:
                if raw_message.startswith(listener.name):
                    return True, None
                if listener.alias:
                    if any(raw_message.startswith(alias) for alias in listener.alias):
                        return True, None
                return False, None

            # 定义一个通用的正则匹配器，根据模式选择 re.match 或 re.search
            def regex_matcher(pattern: str):
                return (re.match if listener.regex_mode == RegexMode.match else re.search)(pattern, raw_message,
                                                                                           listener.regex_flags)

            # 使用正则表达式进行匹配
            matchRes = regex_matcher(listener.name)
            if matchRes:
                return True, matchRes

            if listener.alias:
                for alias in listener.alias:
                    matchRes = regex_matcher(alias)
                    if matchRes:
                        return True, matchRes

            return False, None

        def callFunction(func, origin_func, listener: RegisterBase, matchRes: Union[None, re.Match] = None):
            sig = inspect.signature(origin_func)
            num_params = len(sig.parameters)
            if num_params == 0:
                return func()
            elif num_params == 1:
                return func(self.event)
            elif num_params == 2:
                return func(self.event, listener)
            elif num_params == 3:
                return func(self.event, listener, matchRes)

        if self.event.type == "message":
            break_signal: bool = False
            listeners = ListenerManager.get_listeners_by_type("command")
            for key, value in listeners.items():
                for listener in value:
                    res, matchRes = matchCommand(listener)
                    if res:
                        break_signal = True
                        if callFunction(listener.permission, listener.permission, listener, matchRes):
                            callFunction(listener.func, listener.origin_func, listener, matchRes)
                        break
                if break_signal:
                    break
            if not break_signal:
                logger.info("No command matched")
        return True
