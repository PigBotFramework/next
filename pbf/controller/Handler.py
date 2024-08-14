import json
from .Data import Event
from ..utils.Logging import Logger
from ..setup import ListenerManager

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

        event = Event(**self.data)
        self.event = event
        return event

    def handle(self) -> bool:
        """
        Handle the event.
        :return: bool
        """
        listeners = ListenerManager.get_listeners_by_type(self.event.type)
        for key, value in listeners.items():
            for listener in value:
                if listener.permission(self.event):
                    listener.func(self.event)

        if self.event.type == "message":
            break_signal: bool = False
            listeners = ListenerManager.get_listeners_by_type("command")
            for key, value in listeners.items():
                for listener in value:
                    if self.event.raw_message.startswith(listener.name):
                        break_signal = True
                        if listener.permission(self.event):
                            listener.func(self.event)
                        break
                if break_signal:
                    break
            if not break_signal:
                logger.info("No command matched")
        return True
