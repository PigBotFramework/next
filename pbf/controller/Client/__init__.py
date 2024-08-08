from ... import config, logger
from ..Data import Event
from ...statement.TextStatement import TextStatement
from ...utils.CQCode import CQCode

import requests


class Client:
    def __init__(self, event: Event = None):
        if event is None:
            event = Event()
        self.event: Event = event

    def request_by_event(self, action: str, data: list, addition=None, echo: str = ""):
        if addition is None:
            addition = {}
        request_data = dict()
        for i in data:
            request_data[i] = getattr(self.event, i)
        for i in addition:
            request_data[i] = addition[i]
        return self.request(action, request_data, echo)

    def request(self, action: str, data=None, echo: str = ""):
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
        super().__init__(event)
        self.messages: list = list(messages)

    def getParam(self):
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
        if self.event.group_id is not None:
            data = self.send_to(group_id=self.event.group_id)
        else:
            data = self.send_to(user_id=self.event.user_id)
        if data.get("status") == "success":
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
        logger.debug("Converting to image...")

    def send_to(self, user_id: int = None, group_id: int = None):
        params = self.getParam()

        if user_id is not None:
            return self.request("send_msg", {"user_id": user_id, "message": params})
        elif group_id is not None:
            return self.request("send_msg", {"group_id": group_id, "message": params})
        else:
            raise ValueError("No user_id or group_id specified!")
