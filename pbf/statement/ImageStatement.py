from . import Statement


class ImageStatement(Statement):
    def __init__(self, url: str = 'https://pbf.xzynb.top/statics/image/head.jpg', file: str = 'image.image',
                 type: str = None, cache: int = 0, id: int = 40000, c: int = 2) -> None:
        super().__init__("image", **{
            "url": url,
            "file": file,
            "type": type,
            "cache": cache,
            "id": id,
            "c": c,
        })
