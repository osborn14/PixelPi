class AudioData():
    def __inti__(self):
        self.spectrum_heights = [0] * 16
        self.spectrum_avg = 0
        self.display_mode = 0
        self.server_primary_colors = [0, 0, 0]
        self.server_secondary_colors = [0, 0, 0]
        # self.primary_colors = [0, 0, 0]
        # self.secondary_colors = [0, 0, 0]
        self.music_is_playing = False
