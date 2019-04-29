from Interfaces.FiftyFifty import FiftyFifty
import Keys.Settings as SETTINGS


class FiftyFiftyWhite(FiftyFifty):
    def __init__(self, settings, queue):
        super().__init__(settings, queue)

        self.rgb_pin = settings[SETTINGS.WHITE_PIN]

    def displayLightsFromData(self, data):
        self.pi.set_PWM_dutycycle(self.rgb_pin, data.white)

    def displayAudioLights(self, audio_data):
        server_rgb = audio_data.server_primary_colors

        avg_server_rgb = sum(server_rgb) / len(server_rgb)

        # Strip brightness is the number (between 0 and 1) that determines the intensity of the displayed color
        self.strip_led_brightness = self.calculateStripLEDBrightness(self.strip_led_brightness, audio_data.spectrum_avg) * self.audio_dimmer

        # Temp strip brightness takes the strip brightness and multiplies it by a certain factor,
        # so the displayed color is brighter at lower noise volumes
        temp_strip_led_brightness = self.calculateTempStripLEDBrightness(self.strip_led_brightness, self.strip_led_brightness_multiplier)

        self.pi.set_PWM_dutycycle(self.rgb_pin, avg_server_rgb / 255 * temp_strip_led_brightness)

