import sys, time


class Data:
    def __init__(self, service=None):
        self.service = service
        self.creation_time = time.time()
        self.active = True

    def ensureImportantPropertiesAreSet(self):
        try:
            self.locked
            self.must_be_singular
            self.server_store_last_value

        except AttributeError:
            print("Not all important properties are set! Exiting...")
            sys.exit()

    def getDict(self):
        raise NotImplementedError

    def setDataFromDict(self, json):
        raise NotImplementedError

    def setToDefaults(self):
        raise NotImplementedError
