from Data.Data import Data

import Keys.Audio as AUDIO
import Keys.Settings as SETTINGS

class AudioData(Data):
    def __init__(self, service=None):
        super().__init__(service)

        self.name = SETTINGS.AUDIO_DATA
        self.locked = True
        self.must_be_singular = True
        self.server_store_last_value = False
        self.last_played_time = 0

        self.spectrum_heights = [0] * 16
        self.spectrum_avg = 0
        self.display_mode = 0
        self.server_primary_colors = [0, 0, 0]
        self.server_secondary_colors = [0, 0, 0]
        self.music_is_playing = False

    def getDict(self):
        audio_data_json = {
            SETTINGS.SERVICE: self.service,
            AUDIO.SPECTRUM_AVG: self.spectrum_avg,
            AUDIO.SPECTRUM_HEIGHTS: self.spectrum_heights,
            AUDIO.SPECTRUM_PRIMARY_COLORS: self.server_primary_colors,
            AUDIO.SPECTRUM_SECONDARY_COLORS: self.server_secondary_colors,
            AUDIO.AUDIO_DISPLAY_MODE: self.display_mode,
            SETTINGS.CREATION_TIME: self.creation_time
        }

        return audio_data_json
    
    def setDataFromDict(self, json):
        self.spectrum_heights = json[AUDIO.SPECTRUM_HEIGHTS]
        self.spectrum_avg = json[AUDIO.SPECTRUM_AVG]
        self.display_mode = json[AUDIO.AUDIO_DISPLAY_MODE]
        self.server_primary_colors = json[AUDIO.SPECTRUM_PRIMARY_COLORS]
        self.server_secondary_colors = json[AUDIO.SPECTRUM_SECONDARY_COLORS]
        self.creation_time = json[SETTINGS.CREATION_TIME]
        
    def setToDefaults(self):
        self.spectrum_heights = [0] * 16
        self.spectrum_avg = 0
