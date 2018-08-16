import Application.Common.SettingsConstants as KEY
from Application.Interfaces.Neopixel import Neopixel
import Application.Config as Config


class Settings(object):
    # TODO: Settings should be able to be modified from website
    def __init__(self):
        self.interface_list = list()
        
        # TODO: How should I reference settings text file directory?
        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # settings_file_location = os.path.abspath(
        #     os.path.join(current_directory, os.pardir)) + "/PixelPi/client_settings.txt"
        #
        # try:
        #     settings_file = open(settings_file_location, "r")
        # except IOError:
        #     print("Could not read settings file: " + settings_file_location)
        #     # TODO: Ask user if they want to update settings (AppSetup)
        #     sys.exit()
        #
        # self.settings_file_output = settings_file.readlines()
        # settings_file.close

        self.server_settings = Config.server

        self.client_settings = Config.client

        for settings in Config.neopixel:
            self.interface_list.append(Neopixel(settings))

    def getServerSettings(self):
        return self.server_settings

    def getUniversalClientSettings(self):
        return self.client_settings

    def getInterfaces(self):
        return self.interface_list


# class ClientSettings():
#     def __init__(self, raw_settings_list):
#         raw_settings_processor = RawSettingsProcessor(raw_settings_list)
#
#         self.SERVER_IP_ADDRESS      = raw_settings_processor.getValueFromKey(KEY.SERVER_IP_ADDRESS)
#         self.AUDIO_SERVER_PORT_ONE  = raw_settings_processor.getValueFromKey(KEY.AUDIO_SERVER_PORT_ONE)
#         self.AUDIO_SERVER_PORT_TWO  = raw_settings_processor.getValueFromKey(KEY.AUDIO_SERVER_PORT_TWO)
#         self.PIXEL_PI_SERVER_PORT   = raw_settings_processor.getValueFromKey(KEY.PIXEL_PI_SERVER_PORT)
#         self.NO_DISPLAY_TOLERANCE  = raw_settings_processor.getValueFromKey(KEY.NO_DISPLAY_TOLERANCE)
#
#         self.CURRENT_OS = platform.platform()
#         if "Darwin" not in self.CURRENT_OS and "Windows" not in self.CURRENT_OS:
#             self.IS_TESTING = True
#         else:
#             self.IS_TESTING = False


# class NeopixelSettings():
#     def __init__(self, raw_settings_list):
#         raw_settings_processor = RawSettingsProcessor(raw_settings_list)
#
#         self.MAIN_PIN   = raw_settings_processor.getValueFromKey(KEY.MAIN_PIN)
#         self.LED_COUNT  = raw_settings_processor.getValueFromKey(KEY.LED_COUNT)


class FiftyFiftySettings():
    def __init__(self, raw_settings_list):
        raw_settings_processor = RawSettingsProcessor(raw_settings_list)

        self.STRIP_TYPE = raw_settings_processor.getValueFromKey(KEY.STRIP_TYPE)
        self.RED_PIN    = raw_settings_processor.getValueFromKey(KEY.RED_PIN)
        self.GREEN_PIN  = raw_settings_processor.getValueFromKey(KEY.GREEN_PIN)
        self.BLUE_PIN   = raw_settings_processor.getValueFromKey(KEY.BLUE_PIN)


# class Device():
#     def __init__(self, device_name, device_code, device_type):
#         self.device_name =

