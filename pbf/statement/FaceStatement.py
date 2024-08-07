from . import Statement


class FaceStatement(Statement):
    def __init__(self, face: int) -> None:
        super().__init__("face", **{"id": face})
