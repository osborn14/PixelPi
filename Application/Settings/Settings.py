#!/usr/bin/env python
import os, sys, pigpio, platform
from neopixel import *

class Settings(object):
    ## MAKE A SETTIGS FILE THAT CAN BE UPDATED FROM ANDROID
    def __init__(self):
        ## Get relative path of text file
        current_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file_location = os.path.abspath(os.path.join(current_directory, os.pardir)) + "/PixelPi/client_settings.txt"
        
        try:
            settings_file = open(settings_file_location, "r")
        except IOError:
            print("Could not read settings file: " + settings_file_location)
            sys.exit()
    
        with settings_file:
            for line in settings_file:
                ## A loop and if / elif was used here as opposed to a single pass to allow the use to enter setting in any order they desire
                split_line = line.split(":")
                temp_label = split_line[0].rstrip()
                temp_value = split_line[1].rstrip('\n')

                if temp_label == "ALL Server IPAddress":
                    self.ServerIP = temp_value
                elif temp_label == "LED STRIP Main Red Pin":
                    self.main_red_pin = int(temp_value)
                elif temp_label == "LED STRIP Main Green Pin":
                    self.main_green_pin = int(temp_value)
                elif temp_label == "LED STRIP Main Blue Pin":
                    self.main_blue_pin = int(temp_value)
                elif temp_label =="LED STRIP ADDRESSABLE Pin":
                    self.strip_led_addressable_pin = int(temp_value)
                elif temp_label =="LED STRIP ADDRESSABLE Led Count":
                    self.led_count = int(temp_value)
                elif temp_label == "LED CLOCK TimeZone":
                    self.time_zone = temp_value
                elif temp_label == "PIXEL PI Device Name":
                    self.device_name = temp_value
                elif temp_label == "PIXEL PI Device Code":
                    self.device_code = temp_value
                elif temp_label == "PIXEL PI Device Type":
                    self.device_type = temp_value
                elif temp_label == "PIXEL PI Server Port":
                    self.websocket_server_port = int(temp_value)

        self.current_os = platform.platform()
        if "Darwin" not in self.current_os and "Windows" not in self.current_os:
            self.IN_TESTING_ENVIRONMENT = True
        else:
            self.IN_TESTING_ENVIRONMENT = False

        settings_file.close

    def getDeviceSettings(self):
        if self.device_type == 'NP' or self.device_type == 'N1':
            return NeopixelRunner(self)
        if self.device_type == '50':
            return FiftyFiftyRunner(self)


