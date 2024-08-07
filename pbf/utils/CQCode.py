from ..statement import Statement


class CQCode:
    content: str = None

    def __init__(self, content: str) -> None:
        if content is None:
            raise ValueError("Content cannot be None!")
        self.content = content

    def getArr(self) -> list:
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
            except Exception:
                raise ValueError("Not a valid CQCode!")

        return arr

    def get(self, key: str, index: int = None, type: str = None) -> list:
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
        ret_list: list = []
        for item in self.getArr():
            ret_list.append(Statement('cqcode').set(item))
        return ret_list


if __name__ == "__main__":
    cq_code = CQCode("[CQ:face,id=54][CQ:image,url=azazaz,az=abab]")
    print(cq_code.getArr())
    print(cq_code.get("az"))