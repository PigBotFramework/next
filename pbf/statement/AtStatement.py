from . import Statement


class AtStatement(Statement):
    def __init__(self, qq: int) -> None:
        super().__init__("at", **{"qq": qq})
