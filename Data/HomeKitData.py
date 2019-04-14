from Data.Data import Data

import Keys.Settings as SETTINGS


class HomeKitData(Data):
    def __init__(self, service=None):
        super().__init__(service)

        self.name = SETTINGS.HOMEKIT_DATA
        self.locked = False
        self.must_be_singular = True
        self.server_store_last_value = None

        self.red = 0
        self.green = 0
        self.blue = 0

    def getDict(self):
        data_json = {
            SETTINGS.SERVICE: self.service,
            SETTINGS.RED: self.red,
            SETTINGS.GREEN: self.green,
            SETTINGS.BLUE: self.blue,
        }

        return data_json

    def setDataFromDict(self, json):
        self.red = json[SETTINGS.RED]
        self.green = json[SETTINGS.GREEN]
        self.blue = json[SETTINGS.BLUE]

    def setToDefaults(self):
        self.red = 0
        self.green = 0
        self.blue = 0
