class Statement:
    cqtype: str = None
    statementFlag: bool = False

    def __init__(self, type: str, **kwargs) -> None:
        """
        初始化Statement对象。
        :param type: str CQ类型
        :param kwargs: **dict CQ数据
        """
        self.cqtype = type
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
