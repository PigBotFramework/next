import json
from .Data import Event


class Handler:
    def __init__(self, event_data: str) -> None:
        self.data = json.loads(event_data)
        self.classify()

    def classify(self) -> Event:
        """
        1. ```python
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
                "text": "OneBot is not a bot"
            }
        },
        {
            "type": "image",
            "data": {
                "file_id": "e30f9684-3d54-4f65-b2da-db291a477f16"
            }
        }
    ],
    "alt_message": "OneBot is not a bot[图片]",
    "user_id": "123456788"
}
```

        2. ```python
        {
    "self_id": "123234"
    "time": 1632847927,
    "post_type": "message",
    "message_type": "private",
    "sub_type": "",
    "message_id": "6283",
    "message": [
        {
            "type": "text",
            "data": {
                "text": "OneBot is not a bot"
            }
        },
        {
            "type": "image",
            "data": {
                "file_id": "e30f9684-3d54-4f65-b2da-db291a477f16"
            }
        }
    ],
    "raw_message": "OneBot is not a bot[图片]",
    "user_id": "123456788",
    "sender": {
        "user_id": "123456788",
        "nickname": "海阔天空"
    }
}
```
要求：同时兼容上面的两种格式，将self.data转换为pbf.controller.Data.Event对象，给出代码
        """
        if "self" in self.data:
            self.data["self_id"] = self.data["self"]["user_id"]
            del self.data["self"]

        if "post_type" in self.data:
            self.data["type"] = self.data["post_type"]
            del self.data["post_type"]

        if "message_type" in self.data:
            self.data["detail_type"] = self.data["message_type"]
            del self.data["message_type"]

        if "alt_message" in self.data:
            self.data["raw_message"] = self.data["alt_message"]
            del self.data["alt_message"]

        if "qq.nickname" in self.data:
            self.data["sender"] = {
                "user_id": self.data["user_id"],
                "nickname": self.data["qq.nickname"]
            }
            del self.data["qq.nickname"]

        event = Event(self.data)
        self.event = event
        return event
