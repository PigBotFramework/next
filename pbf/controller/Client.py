"""
# Client包的使用方法

## Msg类的使用

### 构造器定义
```python
Msg(*messages, event: pbf.controller.Data.Event = None)
```
您可以传入多个消息，消息可以是str或Statement对象。str中可以包含CQ码，会自动转为Statement对象。<br>
```python
msg1 = [
    TextStatement("这是一段消息"),
    FaceStatement(114)
]

msg2 = [
    FaceStatement(514),
    "str类型会自动被转为TextStatement",
    TextStatement("这是另一段文本")
]

msg3 = [
    "[CQ:face,id=191]",  # 若str中含有CQ码，会自动被转换！
    TextStatement("这是一段text消息"),
    "这是另一段text消息"
]
```
上面三种传参方式都是可以的

`event`参数是当前正在处理的事件，您可以选择不传入。<br>
如果传入`event`，后续调用`send`方法的时候将会自动选择事件中对应的用户或群聊发送<br>
如果不传入，您需要调用`send_to`方法指定用户或群聊ID并发送

### `send`方法
```python
send(self, retry: int = 0, image: bool = True)
```
- `retry`表示重试次数，`0`表示不重试
- `image`表示是否尝试自动转为图片发送

当`retry`次数耗尽时，若`image`传参为`True`，就会尝试自动将消息转为图片发送。

### `send_to`方法
```python
send_to(self, user_id: int = None, group_id: int = None)
```
顾名思义，您需要传入`user_id`和`group_id`中的至少一项。<br>
如果两者都传入，那么会优先向`user_id`用户发送消息<br>
如果两者都为None，那么会抛出`ValueError("No user_id or group_id specified!")`


##  Client类的使用
Client类用来与OneBot实现直接进行交互，调用接口。Msg类也是继承Client类实现的。

### 构造器
```python
Client(event: pbf.controller.Data.Event = None)
```
`event`参数可以传入，如果不传入，就不能使用`request_by_event`方法

### `request`方法
```python
request(self, action: str, data=None, echo: str = "")
```
**关于每一个参数的详细解释，见[OneBot v12文档](https://12.onebot.dev/connect/data-protocol/action-request/)** <br>
- `action`表示动作名称，如`send_message`
- `data`是动作参数，即OneBot文档中的`params`
- `echo`是回声，可以用于唯一标识一个动作请求

该方法会根据`pbf.config.ob_version`的值自动适配不同的OneBot标准<br>
`pbf.config.ob_version`的可选值有`"v11"`和`"v12"`<br>
返回请求下来的json解码后的数据

### `request_by_event`方法
使用该方法，可以很方便地根据`event`中的数据来自动填充动作参数，比如：
```python
# 下面的例子均采用OneBot v12标准

Client(event).request_by_event("delete_message", ["message_id"])  # 撤回当前事件对应的消息
# 这样可以自动从`event`中提取出`message_id`并发送请求

Client(event).request_by_event("send_message", ["detail_type", "group_id"], {"message":"Hello"})  # 发送消息到当前事件对应的群里
# 这样可以在`detail_type`和`group_id`的基础上，再添加`message`参数发送请求
```
"""


from ..setup import logger, pluginsManager
from .. import config
from .. import version
from .Data import Event
from ..statement.TextStatement import TextStatement
from ..utils.CQCode import CQCode

import requests


class Client:
    def __init__(self, event: Event = None):
        """
        初始化Client。<br>
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
            "PBF-Client": f"PBFNext v{version}",
        }
        req = None
        if config.ob_version == config.OneBotVersion.v11:
            req = requests.post(f"{config.ob_uri}/{action}",
                                json=data,
                                headers=headers)
        elif config.ob_version == config.OneBotVersion.v12:
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
        初始化Msg。<br>
        若使用send方法发送消息，需要传入Event对象。
        :param messages: *list 消息列表。元素可以是str或Statement对象。str中可以包含CQ码，会自动转为Statement对象。
        :param event: Event (可选)Event对象
        """
        super().__init__(event)
        self.messages: list = list(messages)
        if isinstance(self.messages[0], list) or isinstance(self.messages[0], tuple):
            # 有的时候Msg(msg_list, event=event).send()忘加`*`（手动滑稽
            self.messages = list(self.messages[0])

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
        发送消息。<br>
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
        发送消息到指定用户或群。<br>
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
