

class Handler:
    def __init__(self, event_data: dict) -> None:
        self.data = event_data

    def handle(self, request):
        return self.app.handle(request)