"""
# 使用方法
**Config类用于处理配置文件。当用户编辑的配置文件不全时，可以自动根据预置内容返回默认值。**

使用时编写一个`MyConfig`类继承自`Config`，并覆写`originData`属性。<br>
`originData`属性用于存储默认值，实例化时传入的`data`用于存储实际值。<br>

```python
class MyConfig(Config):
    originData = {
        "WindowTitle": {
            "Enable": True,
            "Text": "Hello, World!"
        }
    }

data = {
    "WindowTitle": {}
}  # 我们假设这个data是从某些json配置文件中读取的，用户可能只填写了部分内容

config = MyConfig(data)
print(config.get("WindowTitle.Enable"))
config.set("WindowTitle.Enable", False)
print(config.get("WindowTitle.Enable"))
config.autoComplete()
print(config.get("WindowTitle.Text"))
print(config.data)
```
输出如下
```
True
False
Hello, World!
{'WindowTitle': {'Enable': False, 'Text': 'Hello, World!'}}
```
"""


class ConfigException(Exception): pass


class Config:
    originData = {}

    def __init__(self, data: any) -> None:
        """
        传入`data`数据。`data`用于在后续`get`时提供默认值。
        :param data: any 初始数据
        """
        self.data = data

    def get(self, key: str, defaultValue: any = None, passOnNotExists: bool = False) -> any:
        """
        传入键获取数据。<br>
        如果键不存在，且不传入`defaultValue`，则返回`data`(初始化类时传入的`data`)中对应的默认值。<br>
        `key`参数可以使用`.`分隔，例如`"WindowTitle.Enable"`，表示获取`data["WindowTitle"]["Enable"]`的值。
        :param key: str 键
        :param defaultValue: str (可选)默认值
        :param passOnNotExists: bool (可选)是否忽略不存在的键，如果为False，会抛出`pbf.utils.Config.ConfigException`
        :return: any 数据
        """
        keyList = key.split(".")
        data = self.data
        originData = self.originData

        for item in keyList:
            data = data.get(item)
            originData = originData.get(item)
            if originData is None:
                if not passOnNotExists:
                    raise ConfigException(f"Unknown key {item} in {key}")
                else:
                    return defaultValue
            if data is None:
                if defaultValue is None:
                    data = originData
                else:
                    return defaultValue

        return data

    def set(self, key: str, value: any) -> bool:
        """
        设置数据
        :param key: str 键
        :param value: any 值
        :return: bool True
        """
        keyList = key.split(".")
        data = self.data

        for item in keyList[:-1]:
            if item not in data:
                data[item] = {}
            data = data[item]

        data[keyList[-1]] = value
        return True

    def autoComplete(self) -> None:
        """
        自动填充`data`中不存在的键。
        :return: None
        """
        for key in self.originData:
            if key not in self.data:
                self.data[key] = self.originData[key]
            elif type(self.originData[key]) == dict:
                for subKey in self.originData[key]:
                    if subKey not in self.data[key]:
                        self.data[key][subKey] = self.originData[key][subKey]


if __name__ == "__main__":
    class MyConfig(Config):
        originData = {
            "WindowTitle": {
                "Enable": True,
                "Text": "Hello, World!"
            }
        }

    config = MyConfig({})
    print(config.get("WindowTitle.Enable"))
    config.set("WindowTitle.Enable", False)
    print(config.get("WindowTitle.Enable"))
    config.autoComplete()
    print(config.get("WindowTitle.Text"))
    print(config.data)