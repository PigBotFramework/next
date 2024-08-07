from . import Statement


class XmlStatement(Statement):
    def __init__(self, data: str):
        super().__init__("xml", **{"data": data})
