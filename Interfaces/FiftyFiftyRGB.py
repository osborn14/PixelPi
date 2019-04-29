from Interfaces.FiftyFifty import FiftyFifty
import Keys.Settings as SETTINGS


class FiftyFiftyRGB(FiftyFifty):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)

        self.rgb_pins = {
            SETTINGS.RED: settings[SETTINGS.RED_PIN],
            SETTINGS.GREEN: settings[SETTINGS.GREEN_PIN],
            SETTINGS.BLUE: settings[SETTINGS.BLUE_PIN]
        }

    def displayLightsFromData(self, data):
        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.RED], data.red)
        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.GREEN], data.green)
        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.BLUE], data.blue)

    def displayAudioLights(self, audio_data):
        if self.strip_type == SETTINGS.STRIP_PRIMARY:
            server_rgb = audio_data.server_primary_colors
        elif self.strip_type == SETTINGS.STRIP_SECONDARY:
            server_rgb = audio_data.server_secondary_colors

        # Strip brightness is the number (between 0 and 1) that determines the intensity of the displayed color
        self.strip_led_brightness = self.calculateStripLEDBrightness(self.strip_led_brightness, audio_data.spectrum_avg) * self.audio_dimmer

        # Temp strip brightness takes the strip brightness and multiplies it by a certain factor,
        # so the displayed color is brighter at lower noise volumes
        temp_strip_led_brightness = self.calculateTempStripLEDBrightness(self.strip_led_brightness, self.strip_led_brightness_multiplier)

        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.RED], server_rgb[0] / 255 * temp_strip_led_brightness)
        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.GREEN], server_rgb[1] / 255 * temp_strip_led_brightness)
        self.pi.set_PWM_dutycycle(self.rgb_pins[SETTINGS.BLUE], server_rgb[2] / 255 * temp_strip_led_brightness)
