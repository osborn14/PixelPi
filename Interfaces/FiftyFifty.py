import os, pigpio

from Interfaces.Interface import Interface
import Keys.Settings as SETTINGS


class FiftyFifty(Interface):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)

        # Get pigpiod running on the RPi if it hasn't been done already
        os.system("sudo pigpiod")
        self.pi = pigpio.pi()
        self.strip_type = settings[SETTINGS.STRIP_TYPE]

        # self.strip_led_brightness_multiplier = settings[SETTINGS.BRIGHTNESS_MULTIPLIER]
        # self.audio_dimmer = settings[SETTINGS.AUDIO_DIMMER]

        self.strip_led_brightness = 0
        self.strip_led_brightness_multiplier = 1
        self.audio_dimmer = 1

    def displayLightsFromData(self, data):
        raise NotImplementedError

    def displayAudioLights(self, audio_data):
        raise NotImplementedError

    def calculateStripLEDBrightness(self, strip_led_brightness, avg):
        if 255 * (avg / 32) > strip_led_brightness:
            strip_led_brightness = int(255 * (avg / 32))
        else:
            if strip_led_brightness > 75:
                strip_led_brightness = strip_led_brightness - 2.5
            elif strip_led_brightness > 0:
                strip_led_brightness = strip_led_brightness - 1.0

            if strip_led_brightness < 0:
                strip_led_brightness = 0

        return strip_led_brightness

    def calculateTempStripLEDBrightness(self, strip_led_brightness, strip_led_brightness_multiplier, minimum_brightness=0):
        temp_strip_led_brightness = int(strip_led_brightness_multiplier * strip_led_brightness)

        if temp_strip_led_brightness > 255:
            temp_strip_led_brightness = 255
        elif temp_strip_led_brightness < minimum_brightness:
            temp_strip_led_brightness = minimum_brightness

        return temp_strip_led_brightness
