from functools import wraps
from typing import List

from ..setup import logger, ListenerManager, pluginsManager


def allPermission(_, event):  # 默认权限，需要接收两个实参
    return True

def adminPermission(event):  # 在装饰器中指定的权限，只需要接受`event`参数
    role: str = event.sender.get("role", "member")
    if role == "admin" or role == "owner":
        return True
    return False

def ownerPermission(event):
    if event.sender.get("role", "member") == "owner":
        return True
    return False


class Base:
    name: str = 'Command name'
    description: str = 'Command description'
    permission: callable = allPermission
    usage: str = 'Command usage'
    alias: List[str] = []
    hidden: bool = False
    enabled: bool = True
    type: str = 'command'
    func: callable = None

    def __init__(self, **kwargs):
        """
        Initialize the command information.
        :param kwargs: **dict
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, origin_func):
        if self.enabled:
            logger.debug(f"Registering {self.type} `{self.name}`")
            ListenerManager.add_listener(self.type, pluginsManager.plugin_name, self)

        def try_except_wrapper(*args, **kwargs):
            try:
                return origin_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {self.type} `{self.name}`: {e}")

        func = try_except_wrapper
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
