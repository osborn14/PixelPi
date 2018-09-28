import sys

import Keys.Settings as SETTINGS
from Interfaces.Matrix import Matrix
from Interfaces.Neopixel import Neopixel
from Interfaces.FiftyFifty import FiftyFifty
import Settings.Config as Config


class Settings(object):
    # TODO: Settings should be able to be modified from website
    def getServerSettings(self):
        try:
            self.server_settings = Config.server
        except NameError:
            print("No server settings found!")
            sys.exit()

        return self.server_settings

    def getUniversalClientSettings(self):
        try:
            self.client_settings = Config.client
        except NameError:
            print("No client settings found!")
            sys.exit()

        return self.client_settings[SETTINGS.UNIVERSAL_SETTINGS]

    def getInterfaces(self):
        # TODO: Do check for required settings!
        interface_list = list()
        
        for interface in self.client_settings[SETTINGS.INTERFACE_LIST]:
            if interface[SETTINGS.INTERFACE] == SETTINGS.MATRIX:
                matrix_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_MATRIX,
                    SETTINGS.MILITARY_TIME: False
                }

                matrix_settings = self.getSettingsWithDefault(self.client_settings[SETTINGS.MATRIX],
                                                              matrix_default_settings)
                interface_list.append(Matrix(matrix_settings))

            if interface[SETTINGS.INTERFACE] == SETTINGS.NEOPIXEL:
                # TODO: Create audio dimmer setting,
                neopixel_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_NEOPIXEL,
                    SETTINGS.AUDIO_DIMMER: 1
                }

                neopixel_settings_list = list(
                    map(lambda settings: self.getSettingsWithDefault(settings, neopixel_default_settings),
                        self.client_settings[SETTINGS.NEOPIXEL]))

                neopixel_list = list(map(lambda settings: Neopixel(settings), neopixel_settings_list))
                interface_list.extend(neopixel_list)

            if interface[SETTINGS.INTERFACE] == SETTINGS.FIFTY_FIFTY:
                fifty_fifty_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_FIFTY_FIFTY,
                    SETTINGS.BRIGHTNESS_MULTIPLIER: 1.4,
                    SETTINGS.AUDIO_DIMMER: 1
                }

                fifty_fifty_settings_list = list(
                    map(lambda settings: self.getSettingsWithDefault(settings, fifty_fifty_default_settings),
                        self.client_settings[SETTINGS.FIFTY_FIFTY]))

                fifty_fifty_list = list(map(lambda settings: FiftyFifty(settings), fifty_fifty_settings_list))
                interface_list.extend(fifty_fifty_list)

        if len(interface_list) == 0:
            print("No interfaces detected!")
            sys.exit()

        return interface_list

    def getSettingsWithDefault(self, settings, defaults):
        for key, value in defaults.items():
            if key not in settings:
                settings[key] = value

        return settings

