import Keys.Settings as SETTINGS

from Interfaces.Interface import Interface
from Interfaces.Common import RPiLEDFunctions as led_fx

import board, neopixel


class Neopixel(Interface):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)

        # self.compatible_services = {
        #     SETTINGS.SPECTRUM_ANALYZER: self.displayAudioLights
        # }

        led_pin_mapping = {
            10: board.D10,
            12: board.D12,
            18: board.D18,
            21: board.D21
        }

        # LED strip configuration:
        self.LED_COUNT = settings[SETTINGS.LED_COUNT]  # Number of LED pixels.
        self.LED_PIN = led_pin_mapping[settings[SETTINGS.MAIN_PIN]]  # GPIO pin connected to the pixels (18 uses PWM!).
        self.ORDER = neopixel.GRB

        # Defining some settings
        # self.audio_dimmer = settings[SETTINGS.AUDIO_DIMMER]
        self.audio_dimmer = 1
        self.PAUSE_TIME = 1 / 20
        # self.BAR_RANGE                          = float(self.LED_COUNT / 16)
        self.BAR_RANGE = self.LED_COUNT / 16

        self.non_priority_data_list = list()
        self.main_height_list = [0] * 16

        # Create NeoPixel object with appropriate configuration.
        self.pixels = neopixel.NeoPixel(self.LED_PIN, self.LED_COUNT, brightness=0.2, auto_write=False, pixel_order=self.ORDER)


        # self.frame_start_time = time.time()

    def displayLightsFromData(self, data):
        self.pixels.fill((data.red, data.green, data.blue))
        self.pixels.show()

    def processDataList(self):
        pass

    def displayAudioLights(self, audio_data):
        # TODO: Color dimming should be slower, color should never reach 0
        self.main_height_list = led_fx.getDataListtoPrint(self.main_height_list, audio_data.spectrum_heights)

        if audio_data.display_mode == 2 or audio_data.display_mode == 3:
            lower_main_rgb = audio_data.server_secondary_colors
        else:
            lower_main_rgb = self.blendColors(audio_data.server_primary_colors, [255, 255, 255])

        lower_main_rgb = [0, 0, 0]

        display_rgb = [0] * 3

        for bar_i in range(len(self.main_height_list)):
            for i in range(len(audio_data.server_primary_colors)):
                display_rgb[i] = int(self.audio_dimmer * audio_data.server_primary_colors[i] * self.main_height_list[bar_i] / 32)

            starting_x = int(bar_i * self.BAR_RANGE)
            ending_x = int((bar_i + 1) * self.BAR_RANGE)

            for individual_pixel in range(starting_x, ending_x):
                self.pixels[individual_pixel] = (display_rgb[0], display_rgb[1], display_rgb[2])

        self.pixels.show()



    def runDefaults(self):
        rgb_to_display = self.getRgbToDisplay()

        # Our display loops will expect an array of arrays, so make sure that's always the case
        if not isinstance(rgb_to_display[0], list):
            rgb_to_display = [rgb_to_display]

        x = 0
        while x <= self.LED_COUNT:
            for rgb in rgb_to_display:
                display_color = Color(rgb[0], rgb[1], rgb[2])
                self.strip.setPixelColor(x, display_color)
                x += 1

        # Display strip
        self.strip.show()

    def displayDefaultLights(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

    def blendColors(self, main_rgb, tip_rgb):
        blended_rgb = [0] * 3
        for i in range(len(main_rgb)):
            blended_rgb[i] = (main_rgb[i] + tip_rgb[i]) / 2.0

        return blended_rgb

