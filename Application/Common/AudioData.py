import Application.Common.NetworkCommands as NETWORK

class AudioData():
    def __init__(self):
        self.spectrum_heights = [0] * 16
        self.spectrum_avg = 0
        self.display_mode = 0
        self.server_primary_colors = [0, 0, 0]
        self.server_secondary_colors = [0, 0, 0]
        # self.primary_colors = [0, 0, 0]
        # self.secondary_colors = [0, 0, 0]
        self.music_is_playing = False

    def getAudioJSON(self):
        audio_data_json = {}
        audio_data_json[NETWORK.SPECTRUM_AVG] = self.spectrum_avg
        audio_data_json[NETWORK.SPECTRUM_HEIGHTS] = self.spectrum_heights
        audio_data_json[NETWORK.SPECTRUM_PRIMARY_COLORS] = self.server_primary_colors
        audio_data_json[NETWORK.SPECTRUM_SECONDARY_COLORS] = self.server_secondary_colors
        audio_data_json[NETWORK.AUDIO_DISPLAY_MODE] = self.display_mode

        return audio_data_json
