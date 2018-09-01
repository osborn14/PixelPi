import sys

import Application.Keys.Settings as SETTINGS
from Application.Interfaces.Neopixel import Neopixel
from Application.Interfaces.FiftyFifty import FiftyFifty
import Application.Settings.Config as Config


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
            self.client_settings = Config.clent
        except NameError:
            print("No client settings found!")
            sys.exit()

        return self.client_settings[SETTINGS.UNIVERSAL_SETTINGS]

    def getInterfaces(self):
        interface_list = list()

        if SETTINGS.NEOPIXEL in self.client_settings:
            neopixel_optional_settings = {
                SETTINGS.CODE: SETTINGS.CODE_NEOPIXEL,
                SETTINGS.BRIGHTNESS_MULTIPLIER: 1.4
            }

            neopixel_settings_list = list(
                map(lambda settings: self.getSettingsWithDefault(settings, neopixel_optional_settings),
                    self.client_settings[SETTINGS.NEOPIXEL]))

            neopixel_list = list(map(lambda settings: interface_list.append(Neopixel(settings)), neopixel_settings_list))
            interface_list = interface_list + neopixel_list

        if SETTINGS.FIFTY_FIFTY in self.client_settings:
            fifty_fifty_optional_settings = {
                SETTINGS.CODE: SETTINGS.CODE_FIFTY_FIFTY,
                SETTINGS.BRIGHTNESS_MULTIPLIER: 1.4
            }

            fifty_fifty_settings_list = list(
                map(lambda settings: self.getSettingsWithDefault(settings, fifty_fifty_optional_settings),
                    self.client_settings[SETTINGS.FIFTY_FIFTY]))

            fifty_fifty_list = list(map(lambda settings: interface_list.append(FiftyFifty(settings)), fifty_fifty_settings_list))
            interface_list = interface_list + fifty_fifty_list

        if len(interface_list) == 0:
            print("No interfaces detected!")
            sys.exit()

        return interface_list

    def getSettingsWithDefault(self, settings, defaults):
        for key, value in defaults.items():
            if key not in settings:
                settings[key] = value

        return settings
