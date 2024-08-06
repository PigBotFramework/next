cacheList: dict = {}


def set(key: str, value):
    """
    Set or replace the key.
    :param key: key
    :param value: value
    :return: None
    """
    cacheList[key] = value


def get(key: str, default=None):
    """
    Get the key value.
    :param key: key
    :param default: default value
    :return: value
    """
    return cacheList.get(key, default)


def delete(key: str):
    """
    Delete the key.
    :param key: key
    :return: value
    """
    value = cacheList.get(key)
    cacheList.pop(key)
    return value


def check(key: str):
    """
    Check if the key exists.
    :param key: key
    :return: bool
    """
    return key in cacheList


if __name__ == '__main__':
    set('test', 'test')
    print(get('test'))
    print(delete('test'))
