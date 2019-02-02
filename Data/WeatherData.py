from Data.Data import Data


class WeatherData:
    def __init__(self):
        super().__init__()

        self.priority = False

    def getJson(self):
        raise NotImplementedError

    def setDataFromJson(self, json):
        raise NotImplementedError

    def setToDefaults(self):
        raise NotImplementedError
