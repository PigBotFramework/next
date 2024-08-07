from . import Statement


class TextStatement(Statement):
    def __init__(self, text: str, enter_flag=False) -> None:
        if enter_flag:
            text += '\n'
        self.text = text
        super().__init__("text", **{"text": text})

    def __str__(self):
        return self.text


if __name__ == '__main__':
    stat = TextStatement('azzz')
    print(stat.get())
