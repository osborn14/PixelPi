#!/usr/bin/env python
import os

class Settings(object):
    ## MAKE A SETTIGS FILE THAT CAN BE UPDATED FROM ANDROID
    def __init__(self):
        settings_file_full_path_str = os.path.dirname(os.path.abspath(__file__)) + "/settings.txt"
        try:
            settings_file = open(settings_file_full_path_str, "r")
        except IOError:
            print("Could not read file:" + settings_file_full_path_str)
            sys.exit()
    
        with settings_file:
            for line in settings_file:
                ## A loop and if / elif was used here as opposed to a single pass to allow the use to enter setting in any order they desire
                split_line = line.split(":")
                temp_label = split_line[0].rstrip()
                temp_value = split_line[1].rstrip('\n')

                if temp_label == "ALL Server IPAddress":
                    self.ServerIP = temp_value
                elif temp_label == "ALL Programs to run":
                    self.program_count = temp_value
                elif temp_label == "ALL Main Program":
                    self.MainProgram = temp_value
                elif temp_label == "ALL Alt Program 1":
                    self.AltProgram1 = temp_value
                ## Not a true FPS, but good enough for what I want
                elif temp_label == "ALL Target FPS":
                    self.target_fps = int(temp_value)
                elif temp_label == "LED SPECTRUM ANALYSIS No Display Tolerance":
                    self.no_display_tolerance = float(temp_value)
                elif temp_label == "LED SPECTRUM ANALYSIS Rainbow Speed":
                    self.rainbow_speed = float(temp_value)
                elif temp_label == "LED MATRIX Fade Start Pixel":
                    self.fade_start_pixel = float(temp_value)
                elif temp_label == "LED MATRIX Fade End Pixel":
                    self.fade_end_pixel = float(temp_value)
                elif temp_label == "LED STRIP Main or Tip":
                    self.main_or_tip = temp_value
                elif temp_label == "LED STRIP Main Red Pin":
                    self.main_red_pin = int(temp_value)
                elif temp_label == "LED STRIP Main Green Pin":
                    self.main_green_pin = int(temp_value)
                elif temp_label == "LED STRIP Main Blue Pin":
                    self.main_blue_pin = int(temp_value)
                elif temp_label == "LED STRIP Tip Red Pin":
                    self.tip_red_pin = int(temp_value)
                elif temp_label == "LED STRIP Tip Green Pin":
                    self.tip_green_pin = int(temp_value)
                elif temp_label == "LED STRIP Tip Blue Pin":
                    self.tip_blue_pin = int(temp_value)
                elif temp_label == "LED STRIP Brightness Multiplier":
                    self.led_brightness_multiplier = float(temp_value)
                elif temp_label =="LED STRIP ADDRESSABLE Pin":
                    self.strip_led_addressable_pin = int(temp_value)
                elif temp_label =="LED STRIP ADDRESSABLE Led Count":
                    self.led_count = int(temp_value)
                elif temp_label == "LED CLOCK TimeZone":
                    self.time_zone = temp_value
                elif temp_label == "LED CLOCK Weather API Key":
                    self.api_key = temp_value
                elif temp_label == "LED CLOCK Weather Latitude":
                    self.latitude = float(temp_value)
                elif temp_label == "LED CLOCK Weather Longitude":
                    self.longitude = float(temp_value)
                elif temp_label == "LED CLOCK Military Time":
                    self.military_time_bool = temp_value == "True"
                elif temp_label == "LED CLOCK Default Sunrise Hour":
                    self.default_sunrise_hour = int(temp_value)
                elif temp_label == "LED CLOCK Default Sunrise Minute":
                    self.default_sunrise_minute = int(temp_value)
                elif temp_label == "LED CLOCK Default Sunset Hour":
                    self.default_sunset_hour = int(temp_value)
                elif temp_label == "LED CLOCK Default Sunset Minute":
                    self.default_sunset_minute = int(temp_value)
                elif temp_label == "LED CLOCK Sunrise Dimmer Hours":
                    self.hours_after_sunrise_to_full_brightness = int(temp_value)
                elif temp_label == "LED CLOCK Sunset Dimmer Hours":
                    self.hours_before_sunset_to_start_dimmer = int(temp_value)
                        
        settings_file.close
