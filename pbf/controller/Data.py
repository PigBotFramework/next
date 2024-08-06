class Event:
    time: float = None
    type: str = None
    self_id: int = None
    sub_type: str = None
    message_id: int = None
    detail_type: str = None
    sender: dict = None
    user_id: int = None
    message: list = None
    raw_message: str = None

    def __init__(self, event_data: dict) -> None:
        for key, value in event_data.items():
            setattr(self, key, value)
