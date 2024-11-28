class At1:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print(f"1before {self.a}")
            func(*args, **kwargs)
            print(f"1after {self.b}")
        return wrapper

class At2:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print(f"2before {self.a}")
            print(f"2after {self.b}")
        return wrapper

@At1("a", "b")
@At2("c", "d")
def test():
    print("test")


if __name__ == '__main__':
    test()
