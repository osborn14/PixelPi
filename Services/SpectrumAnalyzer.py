import numpy as np
import pyaudio, math, time, random

import Keys.Settings as SETTINGS
import Keys.Network as NETWORK

from Services.Service import Service
from Data.AudioData import AudioData


class SpectrumAnalyzer(Service):
    def __init__(self, settings):
        super().__init__(settings)

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
        self.calibration_offset_list = [-37, -27, -19, -25, -25, -27, -29, -33, -36, -39, -43, -45, -47, -46, -46]
        self.adjusted_max_values_list = []

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

        self.last_spectrum_avgs = None

        # Below is the equation 20*self.spectrum_groups^x = 22,050 solved for x
        self.fft_grouping_power = math.log(1024)/math.log(self.spectrum_groups)
        self.fft_grouping_power = round(self.fft_grouping_power, 2)

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        pa = pyaudio.PyAudio()
        self.stream = pa.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

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

        pyaudio_audio_data = self.stream.read(self.CHUNK)
        numpy_audio_data = np.fromstring(pyaudio_audio_data, np.int16)

        numpy_fft_data = np.fft.rfft(numpy_audio_data)
        sound_magnitude = np.abs(numpy_fft_data) * 2

        # if sound_magnitude == 0:
        #     return None

        # Turn off divide by zero warning
        np.seterr(divide='ignore')
        sound_db = 20 * np.log10(sound_magnitude / 32768)

        fft_list = sound_db.tolist()

        spectrum_list = self.getAveragedSpectrumData(fft_list)
        calibrated_spectrum_list = self.getCalibratedList(spectrum_list)
        adjusted_spectrum_list = self.getAdjuectedList(calibrated_spectrum_list)

        print(adjusted_spectrum_list)

        spectrum_avg = sum(adjusted_spectrum_list)/len(adjusted_spectrum_list)

        # print(spectrum_list)

        # if spectrum_avg < self.no_display_tolerance:
        #     spectrum_list = [1] * 16
        #
        #     if current_time - self.music_last_played_time > 60:
        #         # Has it been 60 seconds with no activity?  If so, note that music is off for now
        #         self.music_is_playing = False
        #         return None
        #
        # else:
        #     self.music_last_played_time = current_time
        #     self.music_is_playing = True

        new_audio_data = AudioData(SETTINGS.SPECTRUM_ANALYZER)
        new_audio_data.display_mode = self.display_mode
        new_audio_data.spectrum_heights = spectrum_list
        new_audio_data.spectrum_avg = spectrum_avg
        new_audio_data.server_primary_colors = self.main_rgb_current
        new_audio_data.server_secondary_colors = self.secondary_rgb_current
        new_audio_data.music_is_playing = self.music_is_playing

    def getCalibratedList(self, raw_sound_data_list):
        calibrated_list = list(map(lambda zipped_pair: zipped_pair[0] - zipped_pair[1], zip(raw_sound_data_list, self.calibration_offset_list)))
        return calibrated_list

    def getAdjuectedList(self, sound_data_list):
        # adjusted_data_list = list(map())

        return sound_data_list


    def getBroadcastDict(self, audio_data):
        broadcast_dict = {
            SETTINGS.SERVICE: SETTINGS.SPECTRUM_ANALYZER,
            SETTINGS.DATA: audio_data.getDict()
        }

        return broadcast_dict

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

    def getAveragedSpectrumData(self, full_fft_list):
        averaged_spectrum_data = list()

        lower_limit = 0
        for i in range(1, self.spectrum_groups):
            upper_limit = int(math.trunc(i ** self.fft_grouping_power))

            fft_group_list = full_fft_list[lower_limit:upper_limit]
            fft_group_avg = sum(fft_group_list) / len(fft_group_list)

            if fft_group_avg == float("inf") or fft_group_avg == float("-inf"):
                fft_group_avg = self.last_spectrum_avgs[i]
            else:
                fft_group_avg = round(fft_group_avg)

            averaged_spectrum_data.append(fft_group_avg)

            lower_limit = upper_limit

        self.last_spectrum_avgs = averaged_spectrum_data

        return averaged_spectrum_data


class Rainbow:
    def __init__(self, color_multiplier=1):
        self.rgb = [254, 0, 0]
        self.counter = self.decreasing_color = self.increasing_color = 0
        self.color_multiplier = color_multiplier

    def getNextColor(self):
        if self.counter == 0:
            if self.increasing_color == 2:
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
