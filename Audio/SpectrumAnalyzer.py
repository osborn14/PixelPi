import numpy as np
import pyaudio, math, time, random, json

import Keys.Network as NETWORK

from Audio.AudioData import AudioData


class SpectrumAnalyzer(object):
    def __init__(self, settings=None):
        self.color_values_dict = {
            0: [255, 215, 0],
            1: [255, 0, 0],
            2: [0, 255, 0],
            3: [0, 0, 255],
            4: [255, 165, 0],
            5: [34, 139, 34],
            6: [75, 0, 130],
            7: [25, 25, 112]
        }

        self.display_mode_timer_dict = {
            0: 180,
            1: 60,
            2: 60,
            3: 60
        }

        # TODO: Put calibration data here
        self.calibration_data = list()

        self.rainbow = Rainbow()

        self.main_rgb_current = self.main_rgb_to_pursue = [255, 255, 255]
        self.secondary_rgb_current = self.secondary_rgb_to_pursue = [128, 128, 128]

        self.color_change_time = self.display_mode_time = time.time()

        self.music_last_played_time = 0
        self.music_is_playing = False

        self.color_change_duration = 30
        self.display_mode = 0

        self.spectrum_groups = 16
        self.no_display_tolerance = 1.5

        # Below is the equation 20*self.spectrum_groups^x = 22,050 solved for x
        self.fft_grouping_power = math.log(1024)/math.log(self.spectrum_groups)
        self.fft_grouping_power = round(self.fft_grouping_power, 2)

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

    def calculateTransition(self, rgb, rgb_to_pursue):
        if rgb != rgb_to_pursue:
            for i in range(len(rgb)):
                if abs(rgb[i] - rgb_to_pursue[i]) <= 5:
                    rgb[i] = rgb_to_pursue[i]
                elif rgb[i] - rgb_to_pursue[i] > 5:
                    rgb[i] = rgb[i] - 5
                elif rgb[i] - rgb_to_pursue[i] < -5:
                    rgb[i] = rgb[i] + 5

        return rgb

    def update(self):
        current_time = time.time()

        if current_time - self.display_mode_time >= self.display_mode_timer_dict[self.display_mode]:
            self.display_mode = self.display_mode + 1 if self.display_mode >= len(self.display_mode_timer_dict) - 1 else 0
            self.display_mode_time = current_time

        if current_time - self.color_change_time >= self.color_change_duration:
            self.main_rgb_to_pursue = self.color_values_dict[random.randint(0, (len(self.color_values_dict) - 1))]
            self.secondary_rgb_to_pursue = self.color_values_dict[random.randint(0, (len(self.color_values_dict) - 1))]
            self.color_change_time = current_time

        if self.display_mode != 1:
            self.main_rgb_current = self.calculateTransition(self.main_rgb_current, self.main_rgb_to_pursue)
            self.secondary_rgb_current = self.calculateTransition(self.secondary_rgb_current, self.secondary_rgb_to_pursue)
        else:
            self.main_rgb_current = self.secondary_rgb_current = self.rainbow.getNextColor()


        audio_data = self.stream.read(self.CHUNK)
        numpy_audio_data = np.fromstring(audio_data, np.int16)

        numpy_fft_data = np.fft.rfft(numpy_audio_data)
        sound_magnitude = np.abs(numpy_fft_data) * 2
        sound_db = 20 * np.log10(sound_magnitude / 32768)

        fft_list = sound_db.tolist()

        spectrum_list = self.getAveragedSpectrumData(fft_list)
        spectrum_avg = sum(spectrum_list)/len(spectrum_list)

        print(spectrum_list)

        if spectrum_avg < self.no_display_tolerance:
            spectrum_list = [1] * 16

            if current_time - self.music_last_played_time > 60:
                # Has it been 60 seconds with no activity?  If so, note that music is off for now
                self.music_is_playing = False
                return None

        else:
            self.music_last_played_time = current_time
            self.music_is_playing = True

        new_audio_data = AudioData()
        new_audio_data.display_mode = self.display_mode
        new_audio_data.spectrum_heights = spectrum_list
        new_audio_data.spectrum_avg = spectrum_avg
        new_audio_data.server_primary_colors = self.main_rgb_current
        new_audio_data.server_secondary_colors = self.secondary_rgb_current
        new_audio_data.music_is_playing = self.music_is_playing

        return new_audio_data

    def getBroadcastJson(self, audio_data):
        msg = dict()
        msg[NETWORK.COMMAND] = NETWORK.DISPLAY
        msg[NETWORK.MODE] = NETWORK.AUDIO
        msg[NETWORK.AUDIO_DATA] = audio_data.getAudioJSON()

        return json.dumps(msg, ensure_ascii=False)

    def getAveragedSpectrumData(self, full_fft_list):
        averaged_spectrum_data = list()

        lower_limit = 0
        for i in range(1, self.spectrum_groups):
            upper_limit = int(math.trunc(i ** self.fft_grouping_power))

            fft_group_list = full_fft_list[lower_limit:upper_limit]
            fft_group_avg = sum(fft_group_list) / len(fft_group_list)
            fft_group_avg = round(fft_group_avg)
            averaged_spectrum_data.append(fft_group_avg)

            lower_limit = upper_limit

        return averaged_spectrum_data

class Rainbow:
    def __init__(self, color_multiplier=1):
        self.rgb = [254, 0, 0]
        self.counter = self.decreasing_color = self.increasing_color = 0
        self.color_multiplier = color_multiplier

    def getNextColor(self):
        if self.counter == 0:
            if self.ncreasing_color == 2:
                self.increasing_color = 0
            else:
                self.increasing_color = self.decreasing_color + 1

        self.counter += self.color_multiplier
        self.rgb[self.decreasing_color] -= self.color_multiplier
        self.rgb[self.increasing_color] += self.color_multiplier

        if self.counter >= 254:
            self.counter = 0
            self.decreasing_color += 1
            if self.decreasing_color >= 3:
                self.decreasing_color = 0

        return self.rgb


# if __name__ == '__main__':
#
#     audio_app = AudioStream()
#
#     i = 0
#     while True:
#         audio_app.update()
#         time.sleep(0.1)
