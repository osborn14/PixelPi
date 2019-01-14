from Interfaces.Interface import Interface


class Logger(Interface):
    def __init__(self, settings):
        super().__init__(settings)
        self.code = "LG"

    def displayAudioLights(self, audio_data):
        print("Audio data")
        print(audio_data.getAudioJSON())

    def displayNormalLights(self):
        pass
        # print("Display normal lights")

