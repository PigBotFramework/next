class Statement:
    cqtype: str = None
    statementFlag: bool = False

    def __init__(self, type, **kwargs) -> None:
        self.cqtype = type
        for i in kwargs:
            setattr(self, i, kwargs[i])

    def get(self) -> dict:
        arr = {'type': self.cqtype, 'data': {}}
        for i in dir(self):
            if not i.startswith('__') and not callable(getattr(self, i)) and i != 'cqtype':
                arr['data'][i] = getattr(self, i)

        return arr

    def set(self, data: dict):
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
