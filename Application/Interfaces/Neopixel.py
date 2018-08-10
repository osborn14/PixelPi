import time
import Application.Common.SettingsConstants as KEY
from Application.Interfaces.SharedFunctions import RPiLEDFunctions as led_fx
from neopixel import *


class Neopixel():
    def __init__(self, settings):
        # LED strip configuration:
        self.LED_COUNT                          = settings[KEY.LED_COUNT]      # Number of LED pixels.
        LED_PIN                                 = settings[KEY.MAIN_PIN]      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ                             = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA                                 = 5       # DMA channel to use for generating signal (try 5)
        LED_BRIGHTNESS                          = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT                              = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL                             = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        # Defining some settings
        self.STRIP_LED_BRIGHTNESS_MULTIPLIER    = 1.4
        self.LED_DIMMER                         = 0.75
        self.PAUSE_TIME                         = 1 / 20
        self.FADE_START                         = 8
        self.FADE_END                           = 17
        self.BAR_RANGE                          = float(self.LED_COUNT / 16)

        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(150, 18, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()

    def displayAudioLights(self, audio_data):
        # Strip brightness is the actual number (between 0 and 1) that determines the intensity of the displayed color
        self.strip_led_brightness = led_fx.calculateStripLEDBrightness(self.strip_led_brightness * 1.0, audio_data.avg * 1.0)

        # Temp strip brightness takes the strip brightness and multiplies it by a certain factor, so the displayed color is brighter
        # at lower noise volumes
        temp_strip_led_brightness = led_fx.calculateTempStripLEDBrightness(self.strip_led_brightness * 1.0, self.STRIP_LED_BRIGHTNESS_MULTIPLIER * 1.0, 25) * self.LED_DIMMER

        for i in range(len(audio_data.primary_colors)):
            audio_data.primary_colors[i] = audio_data.primary_colors[i] * temp_strip_led_brightness / 255.0

        for bar_i in range(0, len(audio_data.spectrum_heights)):

            upper_transition_range = 0
            if audio_data.spectrum_heights[bar_i] >= self.FADE_START:
                upper_transition_range = audio_data.spectrum_heights[bar_i] - self.FADE_START

            temp_rgb = led_fx.getFadedColors(self.FADE_START, self.FADE_END, upper_transition_range, audio_data.spectrum_heights[bar_i],
                                             0, audio_data.primary_colors, audio_data.primary_colors)

            starting_x = int(bar_i * self.BAR_RANGE)
            ending_x = int((bar_i + 1) * self.BAR_RANGE)

            for individual_pixel in range(starting_x, ending_x):
                display_color = Color(int(temp_rgb[0]), int(temp_rgb[1]), int(temp_rgb[2]))
                self.strip.setPixelColor(individual_pixel, display_color)

        time.sleep(self.PAUSE_TIME)


    def displayHomeLights(self, rgb_values_array):
        i = 0
        while True:
            for rgb in rgb_values_array:
                ## N1, or WS 2811 Neopixels display in GRB, so the order of colors need to be switched
                # if self.SETTINGS.device_type == 'N1':
                #     color_array = [rgb[1], rgb[0], rgb[2]]
                # else:

                color_array = rgb

                self.strip.setPixelColor(i, Color(color_array[0], color_array[1], color_array[2]))

            i = i + 1

            # Display strip
            self.strip.show()

            #if i >= self.LED_COUNT:
            # break;


    def displayDefaultLights(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 25, 0))
        self.strip.show()
        time.sleep(self.PAUSE_TIME * 5)