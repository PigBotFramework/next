"""
# Statement使用方法
您可以通过pbf.statement.Statement快速构建新的Statement，仅需要通过继承pbf.statement.Statement类

下面是一个使用例子
```python
from pbf.statement import Statement

class VideoStatement(Statement):
    def __init__(self, id: int, video_url: str) -> None:
        super().__init__("video", **{"video_url": video_url, "id": id})

# 或者像下面这样定义（更直观，但是IDE可能会要求你调用超类的__init__方法）

class VideoStatement(Statement):
    cqtype: str = "video"
    id: int = None
    video_url: str = None

    def __init__(self, id: int, video_url: str) -> None:
        self.id = id
        self.video_url = video_url
```
然后我们可以在Msg中传入该Statement进行发送
```python
from pbf.controller.Client import Msg
from pbf.statement.TextStatement import TextStatement
from pbf.statement.FaceStatement import FaceStatement
from path.to.your.statement import VideoStatement

msg = [
    TextStatement("这是一段文字"),
    FaceStatement(114),  # 这是一个表情，id为151
    VideoStatement(514, "https://example.com")
]
Msg(*msg).send_to(group_id=114514)
```
这样做会发送这样的一段消息：
```text
这是一段文字[CQ:face,id=114][CQ:video,id=514,video_url=https://example.com]
```


# 为FaceStatement适配Lagrange
如果你在使用Lagrange.OneBot，那你可能需要对FaceStatement进行一些修改来适配Lagrange

FaceStatement的构造是这样的`[CQ:face,id=xxx]`，其中`xxx`为`int`类型，指明表情的ID。<br>
这样做在go-cqhttp中没有任何问题，但是在Lagrange中会引起JSON解析错误，您需要覆写将`id`类型替换为`str` <br>
```python
from pbf.statement import Statement

class FaceStatement(Statement):
    id: str = None
    cqtype = "face"

    def __init__(self, id: int):
        self.id = str(id)
```
"""

class Statement:
    cqtype: str = None
    statementFlag: bool = False

    def __init__(self, cqtype: str, **kwargs) -> None:
        """
        初始化Statement对象。
        :param type: str CQ类型
        :param kwargs: **dict CQ数据
        """
        self.cqtype = cqtype
        for i in kwargs:
            setattr(self, i, kwargs[i])

    def get(self) -> dict:
        """
        获取Statement对象转换为消息链的数据。
        :return: dict
        """
        arr = {'type': self.cqtype, 'data': {}}
        for i in dir(self):
            if not i.startswith('__') and not callable(getattr(self, i)) and i != 'cqtype':
                arr['data'][i] = getattr(self, i)

        return arr

    def set(self, data: dict):
        """
        设置Statement对象。
        The structure of the message chain data:
        {
            "type": "cqtype",
            "data": {
                "key": "value"
            }
        }
        :param data: dict 消息链数据
        :return:
        """
        self.cqtype = data.get('type')
        data = data.get('data')
        for key, value in data.items():
            setattr(self, key, value)
        return self

    def __str__(self):
        return str(self.get())


if __name__ == '__main__':
    stat = Statement('at', qq=123456789)
    print(stat.get())
