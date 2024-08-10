from ...setup import logger, pluginsManager
from ... import config
from ..Data import Event
from ...statement.TextStatement import TextStatement
from ...utils.CQCode import CQCode

import requests


class Client:
    def __init__(self, event: Event = None):
        """
        初始化Client。
        使用request_by_event方法时，需要传入Event对象。
        :param event: Event or None
        :return: None
        """
        if event is None:
            event = Event()
        self.event: Event = event

    def request_by_event(self, action: str, data: list, addition=None, echo: str = ""):
        """
        通过Event对象发送请求。
        :param action: str 请求动作
        :param data: list 每个元素表示从Event对象中获取的参数
        :param addition: dict (可选)附加参数
        :param echo: str (可选)回声
        :return: dict 请求结果
        """
        if self.event is None:
            raise ValueError("No event specified!")
        if addition is None:
            addition = {}
        request_data = dict()
        for i in data:
            request_data[i] = getattr(self.event, i)
        for i in addition:
            request_data[i] = addition[i]
        return self.request(action, request_data, echo)

    def request(self, action: str, data=None, echo: str = ""):
        """
        发送请求。
        :param action: str 请求动作
        :param data: dict (可选)请求参数
        :param echo: (可选)回声
        :return: dict 请求结果
        """
        if data is None:
            data = {}
        headers = {
            "Authorization": "Bearer " + config.ob_access_token,
            "PBF-Client": f"PBFNext v{config.version}",
        }
        req = None
        if config.ob_version == "v11":
            req = requests.post(f"{config.ob_uri}/{action}",
                                json=data,
                                headers=headers)
        elif config.ob_version == "v12":
            req = requests.post(f"{config.ob_uri}/",
                                json={
                                    "action": action,
                                    "params": data,
                                    "echo": echo
                                },
                                headers=headers)
        data = req.json()
        return data


class Msg(Client):
    def __init__(self, *messages, event: Event = None):
        """
        初始化Msg。
        若使用send方法发送消息，需要传入Event对象。
        :param messages: *list 消息列表。元素可以是str或Statement对象。str中可以包含CQ码，会自动转为Statement对象。
        :param event: Event (可选)Event对象
        """
        super().__init__(event)
        self.messages: list = list(messages)

    def getParam(self):
        """
        获取符合OB标准的消息列表。
        :return: list 消息列表
        """
        ret_arr: list = []
        for i in range(len(self.messages)):
            if isinstance(self.messages[i], str):
                if "[CQ:" in self.messages[i]:
                    statements: list = CQCode(self.messages[i]).toStatement()
                    # 将statements插入到self.messages中
                    self.messages.pop(i)
                    self.messages[i:i] = statements
                else:
                    self.messages[i] = TextStatement(self.messages[i])
            ret_arr.append(self.messages[i].get())
        return ret_arr

    def send(self, retry: int = 0, image: bool = True):
        """
        发送消息。
        需要在初始化时传入Event对象，会自动判断发送到群或私聊。
        :param retry: int (可选)重试次数
        :param image: bool (可选)是否尝试发送图片
        :return: dict 请求结果
        """
        if self.event.group_id is not None:
            data = self.send_to(group_id=self.event.group_id)
        else:
            data = self.send_to(user_id=self.event.user_id)
        if data.get("status") == "ok" or data.get("status") == "success":
            return data
        elif data.get("status") == "failed" and retry:
            logger.warning("Failed to send message, retrying...")
            return self.send(retry-1, image)
        elif data.get("status") == "failed" and image:
            logger.warning("Failed to send message, retrying with image...")
            return self.toImage()
        logger.warning("Failed to send message")
        return data

    def toImage(self):
        """
        将消息转为图片发送。
        :return: dict 请求结果
        """
        if not pluginsManager.hasApi("Pillow"):
            logger.error("Pillow not found")
            return {"status": "failed", "message": "Pillow not found"}
        Pillow = pluginsManager.require("Pillow")
        params = self.getParam()
        Pillow.hello()  # TODO to image

    def send_to(self, user_id: int = None, group_id: int = None):
        """
        发送消息到指定用户或群。
        注意：user_id和group_id至少指定一个，都指定时优先向用户ID发送。
        :param user_id: (可选)用户ID
        :param group_id: (可选)群ID
        :return: dict 请求结果
        """
        params = self.getParam()

        if user_id is not None:
            return self.request("send_msg", {"user_id": user_id, "message": params})
        elif group_id is not None:
            return self.request("send_msg", {"group_id": group_id, "message": params})
        else:
            raise ValueError("No user_id or group_id specified!")
