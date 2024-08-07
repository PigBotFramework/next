import json

from . import Statement


class JsonStatement(Statement):
    def __init__(self, json_obj: object):
        super().__init__("json", **{"data": json.dumps(json_obj)})
