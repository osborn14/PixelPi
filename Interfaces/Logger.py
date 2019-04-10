import Keys.Settings as SETTINGS

from Interfaces.Interface import Interface


class Logger(Interface):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)
        self.code = "LG"

        self.compatible_services = {
            SETTINGS.SPECTRUM_ANALYZER: self.displayAudioLights,
            SETTINGS.WEATHER: self.processDataList
        }

    def displayAudioLights(self, audio_data):
        print("Audio data")
        print(audio_data.getDict())

    def runDefaults(self):
        print("Running defaults")
        pass

