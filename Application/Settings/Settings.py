#!/usr/bin/env python
import os, sys, platform

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Application.Common.SettingsKeys as KEY
from Application.Display.Runners import NeopixelRunner, FiftyFiftyRunner


class Settings(object):
    # TODO: Settings should be able to be modified from website
    def __init__(self):
        self.runners_list = list()
        
        # TODO: How should I reference settings text file directory?
        current_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file_location = os.path.abspath(
            os.path.join(current_directory, os.pardir)) + "/PixelPi/client_settings.txt"

        try:
            settings_file = open(settings_file_location, "r")
        except IOError:
            print("Could not read settings file: " + settings_file_location)
            # TODO: Ask user if they want to update settings (AppSetup)
            sys.exit()

        self.settings_file_output = settings_file.readlines()
        settings_file.close

    def processSettings(self):
        settings_objects = list()

        i = 0
        while i < len(self.settings_file_output):
            if "DEVICE SETTINGS" in self.settings_file_output[i]:
                split_line = self.settings_file_output[i].split(":")
                line_value = split_line[1].rstrip('\n')

                device_type = line_value
                raw_settings_list = list()

                i+=1

                while True:
                    if "DEVICE SETTINGS" in self.settings_file_output[i]:
                        if device_type == "CL":
                            self.client_settings = ClientSettings(raw_settings_list)
                            
                        #elif device_type == "MA":
                            # TODO: Add matrix settings & runner
                        
                        elif device_type == "NP":
                            settings = NeopixelSettings(raw_settings_list)
                            runner = NeopixelRunner(settings)
                            
                        elif device_type == "50":
                            settings = FiftyFiftySettings(raw_settings_list)
                            runner = FiftyFiftyRunner(settings)

                        else:
                            print("Device not recognized!")
                            # TODO: Throw unrecognized device error

                        settings_objects.append(settings)
                        self.runners_list.append(runner)

                        break;

                    else:
                        raw_settings_list.append(self.settings_file_output[i])
                        i+=1

    def getRunners(self):
        return self.runners_list


class ClientSettings():
    def __init__(self, raw_settings_list):
        raw_settings_processor = RawSettingsProcessor(raw_settings_list)

        self.SERVER_IP_ADDRESS      = raw_settings_processor.getValueFromKey(KEY.SERVER_IP_ADDRESS)
        self.AUDIO_SERVER_PORT_ONE  = raw_settings_processor.getValueFromKey(KEY.AUDIO_SERVER_PORT_ONE)
        self.AUDIO_SERVER_PORT_TWO  = raw_settings_processor.getValueFromKey(KEY.AUDIO_SERVER_PORT_TWO)
        self.PIXEL_PI_SERVER_PORT   = raw_settings_processor.getValueFromKey(KEY.PIXEL_PI_SERVER_PORT)
        self. NO_DISPLAY_TOLERANCE  = raw_settings_processor.getValueFromKey(KEY.NO_DISPLAY_TOLERANCE)

        self.CURRENT_OS = platform.platform()
        if "Darwin" not in self.CURRENT_OS and "Windows" not in self.CURRENT_OS:
            self.IS_TESTING = True
        else:
            self.IS_TESTING = False

class NeopixelSettings():
    def __init__(self, raw_settings_list):
        raw_settings_processor = RawSettingsProcessor(raw_settings_list)

        self.MAIN_PIN   = raw_settings_processor.getValueFromKey(KEY.MAIN_PIN)
        self.LED_COUNT  = raw_settings_processor.getValueFromKey(KEY.LED_COUNT)

class FiftyFiftySettings():
    def __init__(self, raw_settings_list):
        raw_settings_processor = RawSettingsProcessor(raw_settings_list)

        self.RED_PIN    = raw_settings_processor.getValueFromKey(KEY.RED_PIN)
        self.GREEN_PIN  = raw_settings_processor.getValueFromKey(KEY.GREEN_PIN)
        self.BLUE_PIN   = raw_settings_processor.getValueFromKey(KEY.BLUE_PIN)


# class Device():
#     def __init__(self, device_name, device_code, device_type):
#         self.device_name =


def getDeviceSettings(self):
    if self.device_type == 'NP' or self.device_type == 'N1':
        return NeopixelRunner(self)
    if self.device_type == '50':
        return FiftyFiftyRunner(self)


class RawSettingsProcessor():
    def __init__(self, raw_settings_list):
        self.raw_settings_dict = {}

        for setting in raw_settings_list:
            split_line = setting.split(":")
            temp_key = split_line[0].rstrip()
            temp_value = split_line[1].rstrip('\n')

            self.raw_settings_dict[temp_key] = temp_value


    def getValueFromKey(self, key):
        # TODO: Throw error here if key doesn't exist
        return self.raw_settings_dict[key]
