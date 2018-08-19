import Application.Keys.Settings as SETTINGS


class Interface():
    def __init__(self, settings):
        self.unique_identifier = settings[SETTINGS.UNIQUE_IDENTIFIER]
        self.code = settings[SETTINGS.CODE]
        self.description = settings[SETTINGS.DESCRIPTION]

    def getInterfaceJson(self):
        interface_settings_dict = {
            SETTINGS.UNIQUE_IDENTIFIER: self.unique_identifier,
            SETTINGS.CODE: self.code,
            SETTINGS.DESCRIPTION: self.description
        }

        return interface_settings_dict

    def displayAudioLights(self):
        raise NotImplementedError