class ConfigException(Exception): pass


class Config:
    originData = {}

    def __init__(self, data) -> None:
        self.data = data

    def get(self, key: str, defaultValue: any = None, passOnNotExists: bool = False) -> any:
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

    def set(self, key, value: any) -> bool:
        keyList = key.split(".")
        data = self.data

        for item in keyList[:-1]:
            if item not in data:
                data[item] = {}
            data = data[item]

        data[keyList[-1]] = value
        return True

    def autoComplete(self) -> None:
        for key in self.originData:
            if key not in self.data:
                self.data[key] = self.originData[key]
            elif type(self.originData[key]) == dict:
                for subKey in self.originData[key]:
                    if subKey not in self.data[key]:
                        self.data[key][subKey] = self.originData[key][subKey]

    def __del__(self):
        # self.save()
        pass


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