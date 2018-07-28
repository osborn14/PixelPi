#!/usr/bin/env python
import os, sys, pigpio, platform
from neopixel import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Application.Common.SettingsKeys as KEY


class Settings(object):
    #TODO: Settings should be able to be modified from website
    def __init__(self):
        # TODO: How should I reference settings file?
        ## Get relative path of text file
        current_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file_location = os.path.abspath(
            os.path.join(current_directory, os.pardir)) + "/PixelPi/client_settings.txt"

        try:
            settings_file = open(settings_file_location, "r")
        except IOError:
            print("Could not read settings file: " + settings_file_location)
            sys.exit()

        settings_file_output = settings_file.readlines()
        settings_file.close

        # TODO: Find all the occurance of a given string in the text file
        settings_objects = list()

        i = 0
        while i < len(settings_file_output):
            if "DEVICE SETTINGS" in settings_file_output[i]:
                split_line = settings_file_output[i].split(":")
                line_value = split_line[1].rstrip('\n')

                device_type = line_value
                raw_settings_list = list()

                i+=1

                while True:
                    if "DEVICE SETTINGS" in settings_file_output[i]:
                        if device_type == "CL":
                            settings_objects.append(ClientSettings(raw_settings_list))

                        elif device_type == "NP":
                            settings_objects.append(NeopixelSettings(raw_settings_list))

                        break;

                    else:
                        raw_settings_list.append(settings_file_output[i])
                        i+=1


class ClientSettings():
    def __init__(self, raw_settings_list):
        rawSettingsProcessor = RawSettingsProcessor(raw_settings_list)

        self.SERVER_IP_ADDRESS      = rawSettingsProcessor(KEY.SERVER_IP_ADDRESS)
        self.AUDIO_SERVER_PORT_ONE  = rawSettingsProcessor(KEY.AUDIO_SERVER_PORT_ONE)
        self.AUDIO_SERVER_PORT_TWO  = rawSettingsProcessor(KEY.AUDIO_SERVER_PORT_TWO)
        self.PIXEL_PI_SERVER_PORT   = rawSettingsProcessor(KEY.PIXEL_PI_SERVER_PORT)

        self.CURRENT_OS = platform.platform()
        if "Darwin" not in self.CURRENT_OS and "Windows" not in self.CURRENT_OS:
            self.IS_TESTING = True
        else:
            self.IS_TESTING = False

class NeopixelSettings():
    def __init__(self, raw_settings_list):
        rawSettingsProcessor = RawSettingsProcessor(raw_settings_list)

        self.MAIN_PIN   = rawSettingsProcessor(KEY.MAIN_PIN)
        self.LED_COUNT  = rawSettingsProcessor(KEY.LED_COUNT)

class FiftyFiftySettings():
    def __init__(self, raw_settings_list):
        rawSettingsProcessor = RawSettingsProcessor(raw_settings_list)

        self.RED_PIN    = rawSettingsProcessor(KEY.RED_PIN)
        self.GREEN_PIN  = rawSettingsProcessor(KEY.GREEN_PIN)
        self.BLUE_PIN   = rawSettingsProcessor(KEY.BLUE_PIN)


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
