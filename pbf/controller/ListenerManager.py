from ..utils.Logging import Logger

logger = Logger(__name__)

command_listeners = {}
message_listeners = {}
notice_listeners = {}
request_listeners = {}
meta_listeners = {}


class ListenerManager:
    @staticmethod
    def set_listener(event_type: str, listener_dict: dict):
        """
        Set the listener dict.
        :param event_type: str event type
        :param listener_dict: dict listener dict
        :return:
        """
        global command_listeners, message_listeners, notice_listeners, request_listeners, meta_listeners
        if event_type == "command":
            command_listeners = listener_dict
        elif event_type == "message":
            message_listeners = listener_dict
        elif event_type == "notice":
            notice_listeners = listener_dict
        elif event_type == "request":
            request_listeners = listener_dict
        elif event_type == "meta":
            meta_listeners = listener_dict
        else:
            raise ValueError("Invalid event type")

    @staticmethod
    def add_listener(event_type: str, plugin_name: str, listener):
        """
        Add a listener.
        :param event_type: str event type
        :param plugin_name: str plugin name
        :param listener: object listener
        :return:
        """
        listeners = ListenerManager.get_listeners_by_type(event_type)
        if plugin_name not in listeners:
            listeners[plugin_name] = []
        listeners[plugin_name].append(listener)
        ListenerManager.set_listener(event_type, listeners)

    @staticmethod
    def get_listeners_by_plugin_name(plugin_name: str):
        """
        Get listeners by plugin name.
        :param plugin_name: str plugin name
        :return: list
        """
        return command_listeners.get(plugin_name, []) + \
            message_listeners.get(plugin_name, []) + \
            notice_listeners.get(plugin_name, []) + \
            request_listeners.get(plugin_name, []) + \
            meta_listeners.get(plugin_name, [])

    @staticmethod
    def get_listeners_by_type(event_type: str):
        """
        Get listeners by type.
        :param event_type: str event type
        :return: list
        """
        if event_type == "command":
            return command_listeners
        elif event_type == "message":
            return message_listeners
        elif event_type == "notice":
            return notice_listeners
        elif event_type == "request":
            return request_listeners
        elif event_type == "meta":
            return meta_listeners
        else:
            return []

    @staticmethod
    def remove_listener_by_plugin_name(plugin_name: str):
        """
        Remove listeners by plugin name.
        :param plugin_name: str plugin name
        :return: None
        """
        global command_listeners, message_listeners, notice_listeners, request_listeners, meta_listeners
        for listeners in [command_listeners, message_listeners, notice_listeners, request_listeners, meta_listeners]:
            if plugin_name in listeners:
                listeners.pop(plugin_name)
        ListenerManager.set_listener("command", command_listeners)
        ListenerManager.set_listener("message", message_listeners)
        ListenerManager.set_listener("notice", notice_listeners)
        ListenerManager.set_listener("request", request_listeners)
        ListenerManager.set_listener("meta", meta_listeners)
