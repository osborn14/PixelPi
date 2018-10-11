import Keys.Settings as SETTINGS

class Defaults:
    def __init__(self):
        self.default_settings_dict = {
            SETTINGS.SERVER: {

            },
            SETTINGS.MATRIX: {
                SETTINGS.CODE: SETTINGS.CODE_MATRIX,
                SETTINGS.MILITARY_TIME: False
            },
            # TODO: Create audio dimmer setting
            SETTINGS.NEOPIXEL: {
                SETTINGS.CODE: SETTINGS.CODE_NEOPIXEL,
                SETTINGS.AUDIO_DIMMER: 1
            },
            SETTINGS.FIFTY_FIFTY: {
                SETTINGS.CODE: SETTINGS.CODE_FIFTY_FIFTY,
                SETTINGS.BRIGHTNESS_MULTIPLIER: 1.4,
                SETTINGS.AUDIO_DIMMER: 1
            }
        }

    def getSettingsWithDefaults(self, settings):
        service_type = settings[SETTINGS.INTERFACE]

        updated_settings = list(
            map(lambda settings: self.insertValueIfItDoesntExist(settings, self.default_settings_dict[service_type]),
                settings[SETTINGS.NEOPIXEL]))

        return updated_settings

    def insertValueIfItDoesntExist(self, settings, defaults):
        for key, value in defaults.items():
            if key not in settings:
                settings[key] = value

        return settings

