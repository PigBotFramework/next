class Event:
    time: float = None
    type: str = None
    self_id: int = None
    sub_type: str = None
    message_id: int = None
    detail_type: str = None
    sender: dict = None
    user_id: int = None
    group_id: int = None
    message: list = None
    raw_message: str = None
    message_list: list = None

    def __init__(self, **event_data) -> None:
        """
        初始化Event对象。
        :param event_data: **dict 事件数据
        """
        if event_data is None:
            event_data = {}
        for key, value in event_data.items():
            setattr(self, key, value)
