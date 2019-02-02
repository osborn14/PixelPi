#!/usr/bin/python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics, RGBMatrixOptions, RGBMatrix
import time
import datetime
import calendar
import os
import random
import RPiLEDFunctions as led_fx
import RPiClockFunctions as clock_fx
from Settings import Settings
from Animation import Animation, RGBpixel
from socket import socket,AF_INET,SOCK_DGRAM
from Weather import Weather, getWeatherData

class LEDClock(SampleBase):
    def __init__(self, *args, **kwargs):
        super(LEDClock, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/Documents/rpi-rgb-led-matrix-master/fonts/7x13B.bdf")
        font_small = graphics.Font()
        font_small.LoadFont("/home/pi/Documents/rpi-rgb-led-matrix-master/fonts/6x10.bdf")

        settings_file = Settings()
        os.environ['TZ'] = settings_file.time_zone
        
        sock = led_fx.connectToServer(settings_file, 8080)

        ## NEED TO PLACE THIS CODE IN THE WEATHER OBJECT
        no_display_tolerance = settings_file.no_display_tolerance
        military_time_bool = settings_file.military_time_bool
        
        
        fetch_weather_time = time.time()
        colon_counter = 0
        firsttime = True
        refresh_pause = .5
        dimmer_minimum = 0.02
        music_detected_counter = 0

        while True:
            datalist = led_fx.receiveAndCleanData(sock, 17)
            if not datalist:
                datalist = [1] * 17 
                sock = led_fx.connectToServer(settings_file, 8080)
            
            avg = led_fx.getAverageofListValues(datalist, 1, 17)
            
            music_detected_counter = clock_fx.getTimeCounter(avg, no_display_tolerance, music_detected_counter)
            if music_detected_counter >+ 2:
                break;
            
            if time.time() - fetch_weather_time >= 1800 or firsttime == True:
                fetch_weather_time = time.time()
                weather_data = getWeatherData()
                
                firsttime = False
                
            ## Create time class
            current_datetime = datetime.datetime.now()
            current_hour = int(current_datetime.hour)
            current_minute = int(current_datetime.minute)
            
            current_month = str(current_datetime.month)
            current_day = str(current_datetime.day)
            
            current_date = datetime.date.today()
            day_of_the_week = calendar.day_name[current_date.weekday()]
            
            day_of_the_week_abbreviation = day_of_the_week[:3]
            todays_date = day_of_the_week_abbreviation + " " + current_month + "/" + current_day

            
            dimmer = clock_fx.calculateDimmer(current_hour, current_minute, weather_data.sunrise_hour, weather_data.sunrise_minute, weather_data.hours_after_sunrise_to_full_brightness, weather_data.sunset_hour, weather_data.sunset_minute, weather_data.hours_before_sunset_to_start_dimmer, dimmer_minimum)
            isDay = clock_fx.getIsDay(dimmer, dimmer_minimum)
            
            ################ TESTING VARIABLES ###################
            isDay = isDay
            weather_condition = weather_data.weather_condition
            ####################### END ##########################
            
            animation_to_draw = []
            animation = Animation(51, 2)
            color_scheme = clock_fx.getColorScheme(weather_condition, dimmer, isDay)
            MAIN_COLOR = color_scheme[0]
            SUB_COLOR = color_scheme[1]
            
            animation_to_draw = animation.drawWeather(weather_condition, dimmer, isDay)

            colon_or_space = clock_fx.getColonorSpace(refresh_pause, colon_counter)
            colon_counter = colon_counter + 1 if colon_counter < 2 else 0

            am_or_pm = clock_fx.AMorPM(current_hour, military_time_bool)
            current_hour = clock_fx.getCurrentHour(current_hour, military_time_bool)

            current_hour_str = str(current_hour)
            current_minute_str = str(current_minute)
            
            if len(current_hour_str) == 1:
                current_hour_str = "0" + current_hour_str
            
            if len(current_minute_str) == 1:
                current_minute_str = "0" + current_minute_str
        
            current_time_str = current_hour_str + colon_or_space + current_minute_str + am_or_pm

            offscreen_canvas.Clear()
            
            for i in range(len(animation_to_draw)):
                pixel = animation_to_draw[i]
                offscreen_canvas.SetPixel(pixel.x, pixel.y, pixel.rgb[0], pixel.rgb[1], pixel.rgb[2])

            graphics.DrawText(offscreen_canvas, font, 0, 22, SUB_COLOR, todays_date)
            graphics.DrawText(offscreen_canvas, font, 0, 10, MAIN_COLOR, current_time_str)
            
##            if weather_data.good_weather_fetch:
            static_text = str(weather_data.current_temperature) + "F " + weather_data.weather_condition
            graphics.DrawText(offscreen_canvas, font_small, 0, 31, MAIN_COLOR, static_text)

            self.matrix.SwapOnVSync(offscreen_canvas)
            # time.sleep(refresh_pause)

## Main function
if __name__ == "__main__":
    led_clock = LEDClock()
    if (not led_clock.process()):
        led_clock.print_help()
