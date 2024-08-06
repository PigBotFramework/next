from functools import wraps
from typing import List

from .. import logger, ListenerManager, pluginsManager


class Base:
    name: str = 'Command name'
    description: str = 'Command description'
    permission: str = 'cmd.permission.cmdname'
    usage: str = 'Command usage'
    alias: List[str] = []
    hidden: bool = False
    enabled: bool = True
    type: str = 'command'
    func = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, func):
        logger.debug(f"Registering {self.type} `{self.name}`")
        ListenerManager.add_listener(self.type, pluginsManager.plugin_name, self)
        self.func = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"<{self.type}> {self.name} called")
            return func(*args, **kwargs)

        return wrapper


class Command(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "command"


class Message(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "message"


class Notice(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "notice"


class Request(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "request"


class Meta(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "meta"
