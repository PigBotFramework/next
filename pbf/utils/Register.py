import re
import time
from enum import unique, Enum
from functools import wraps
from typing import List

from ..setup import logger, ListenerManager, pluginsManager
from ..error import LimitExceedError


def allPermission(*_):  # 默认权限，需要接收两个实参
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

def default_callback(event, func):
    raise LimitExceedError(f"User {event.user_id} exceeded the limit of {func.__name__}.")


class Limit:
    def __init__(self, duration, times, user=None, callback=None):
        """
        限制指令执行频率
        :param duration: int 限制时间
        :param times: int 限制次数
        :param user: str/int/None (可选)用户ID
        :param callback: Callable (可选)回调函数
        """
        self.duration = duration
        self.times = times
        self.user = user
        self.call_count = {}
        self.callback = callback or default_callback

    def __call__(self, origin_func):
        @wraps(origin_func)
        def limit_wrapper(*args, **kwargs):
            # 假设第一个参数是event，且event有user_id属性
            event = args[0] if args else None
            user_id = event.user_id if event else None
            current_time = time.time()
            if self.user is not None:
                user_id = self.user

            if user_id not in self.call_count:
                self.call_count[user_id] = []

            # 移除过期的调用记录
            self.call_count[user_id] = [
                timestamp for timestamp in self.call_count[user_id]
                if current_time - timestamp < self.duration
            ]

            # 检查调用次数
            if len(self.call_count[user_id]) < self.times:
                self.call_count[user_id].append(current_time)
                return origin_func(*args, **kwargs)
            else:
                # logger.warning(f"User {user_id} exceeded the limit of {origin_func.__name__}.")
                return self.callback(event, origin_func)  # 调用回调函数

        return limit_wrapper


@unique
class RegexMode(Enum):
    match = "match"
    search = "search"
    none = "none"


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
    regex_mode: RegexMode = RegexMode.none
    regex_flags = re.I
    regex_data = None
    origin_func: callable = None

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
        self.origin_func = origin_func
        self.func = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"<{self.type}> {self.name} called")
            return func(*args, **kwargs)

        return wrapper

    def __str__(self):
        return f"<{self.type}Listener \"{self.name}\" call:{self.origin_func.__name__}>"


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
