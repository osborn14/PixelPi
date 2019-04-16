import os, pigpio

from Interfaces.Interface import Interface
from Interfaces.Common import RPiLEDFunctions as led_fx
import Keys.Settings as SETTINGS


class FiftyFifty(Interface):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)

        # Get pigpiod running on the RPi if it hasn't been done already
        os.system("sudo pigpiod")
        self.pi = pigpio.pi()
        self.strip_type = settings[SETTINGS.STRIP_TYPE]
        self.rgb_pins = [settings[SETTINGS.RED_PIN], settings[SETTINGS.GREEN_PIN], settings[SETTINGS.BLUE_PIN]]
        # self.strip_led_brightness_multiplier = settings[SETTINGS.BRIGHTNESS_MULTIPLIER]
        # self.audio_dimmer = settings[SETTINGS.AUDIO_DIMMER]

        self.strip_led_brightness_multiplier = 1
        self.audio_dimmer = settings[SETTINGS.AUDIO_DIMMER]

    def displayAudioLights(self, audio_data):
        if self.strip_type == SETTINGS.STRIP_PRIMARY:
            server_rgb = audio_data.server_primary_colors
        elif self.strip_type == SETTINGS.STRIP_SECONDARY:
            server_rgb = audio_data.server_secondary_colors

        # Strip brightness is the number (between 0 and 1) that determines the intensity of the displayed color
        self.strip_led_brightness = led_fx.calculateStripLEDBrightness(self.strip_led_brightness, audio_data.spectrum_avg) * self.audio_dimmer

        # Temp strip brightness takes the strip brightness and multiplies it by a certain factor,
        # so the displayed color is brighter at lower noise volumes
        temp_strip_led_brightness = led_fx.calculateTempStripLEDBrightness(self.strip_led_brightness,
                                                                           self.strip_led_brightness_multiplier)

        for i in range(0, 3):
            self.pi.set_PWM_dutycycle(self.rgb_pins[i], server_rgb[i] / 255 * temp_strip_led_brightness)

    def displayNormalLights(self):
        rgb_to_display = self.getRgbToDisplay()

        for i in range(len(self.rgb_pins)):
            self.pi.set_PWM_dutycycle(self.rgb_pins[i], rgb_to_display[i])
