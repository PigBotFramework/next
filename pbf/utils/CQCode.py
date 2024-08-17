from ..statement import Statement


class CQCode:
    content: str = None

    def __init__(self, content: str) -> None:
        """
        初始化CQCode对象。
        :param content: str CQCode内容
        """
        if content is None:
            raise ValueError("Content cannot be None!")
        self.content = content

    def getArr(self) -> list:
        """
        获取CQCode完整数组。
        :return: List[dict]
        """
        arr: list = []

        left: list = self.content.split("[")
        del left[0]
        for i in left:
            try:
                right: list = i.split("]")[0].split(",")
                cqDict: dict = {"type": "cqcode", "data": {}}
                for j in right:
                    if j == right[0]:
                        cqDict["type"] = j.split(":")[1]
                    else:
                        tmp_str = j.split("=")
                        cqDict["data"][tmp_str[0]] = tmp_str[1]
                arr.append(cqDict)
            except Exception as exc:
                raise ValueError("Not a valid CQCode!") from exc

        return arr

    def get(self, key: str, index: int = None, type: str = None) -> list:
        """
        获取CQCode数组中的数据。
        :param key: str 键
        :param index: int (可选)第几个CQCode，不传则从所有cqcode中寻找
        :param type: str (可选)CQCode类型，不传则从所有cqcode中寻找
        :return: list
        """
        arr: list = []
        CQArr: list = self.getArr()

        if index is not None:
            if len(CQArr) > index:
                return [CQArr[index].get("data").get(key)]
            else:
                # raise IndexError("Index out of range!")
                return []

        elif type is not None:
            for i in CQArr:
                if i.get("type") == type:
                    arr.append(i.get("data").get(key))

        else:
            for i in CQArr:
                if i.get("data").get(key) is not None:
                    arr.append(i.get("data").get(key))

        return arr

    def toStatement(self):
        """
        转换为Statement对象。
        :return: Statement
        """
        ret_list: list = []
        for item in self.getArr():
            ret_list.append(Statement('cqcode').set(item))
        return ret_list


if __name__ == "__main__":
    cq_code = CQCode("[CQ:face,id=54][CQ:image,url=url_test,arg=arg_test]")
    print(cq_code.getArr())
    print(cq_code.get("az"))
