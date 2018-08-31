import os, pigpio

from Application.Interfaces.Common import RPiLEDFunctions as led_fx
from Application.Keys import Settings as KEY


class FiftyFifty():
    def __init__(self, settings):
        super().__init__(settings)

        ## Get pigpiod running on the RPi if it hasn't been done already
        os.system("sudo pigpiod")
        self.pi = pigpio.pi()
        self.strip_type = settings.STRIP_TYPE
        self.rgb_pins = [settings.RED_PIN, settings.GREEN_PIN, settings.BLUE_PIN]

    def displayAudioLights(self, audio_data):
        if self.strip_type == KEY.STRIP_PRIMARY:
            server_rgb = audio_data.server_primary_colors
        elif self.strip_type == KEY.STRIP_SECONDARY:
            server_rgb = audio_data.server_secondary_colors

        ## Strip brightness is the number (between 0 and 1) that determines the intensity of the displayed color
        strip_led_brightness = led_fx.calculateStripLEDBrightness(strip_led_brightness, audio_data.spectrum_avg)
        ## Temp strip brightness takes the strip brightness and multiplies it by a certain factor, so the displayed color is brighter
        ## at lower noise volumes
        temp_strip_led_brightness = led_fx.calculateTempStripLEDBrightness(strip_led_brightness,
                                                                           strip_led_brightness_multiplier)

        for i in range(0, 3):
            self.pi.set_PWM_dutycycle(self.rgb_pins[i], server_rgb[i] / 255 * temp_strip_led_brightness)

    def displayNormalLights(self):
        if self.checkForTaskToDisplay():
            rgb_to_display = self.display_task.getRgbToDisplay()
        else:
            rgb_to_display = [0, 0, 0]

        for i in range(len(self.rgb_pins)):
            self.pi.set_PWM_dutycycle(self.rgb_pins[i], rgb_to_display[i])