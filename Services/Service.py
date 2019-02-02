class Service:
    def __init__(self, settings):
        self.settings = settings

    def update(self):
        raise NotImplementedError

    def getBroadcastDict(self):
        raise NotImplementedError
