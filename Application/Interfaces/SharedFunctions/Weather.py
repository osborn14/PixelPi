#!/usr/bin/python
import pyowm
import datetime
from Settings import Settings

#fetch user settings using the Settings class
settings_file = Settings()
API_KEY = settings_file.api_key
lat = settings_file.latitude
lon = settings_file.longitude
owm = pyowm.OWM(API_KEY)


class Weather(object):
    def __init__(self, api_weather_details=None):
        self.hours_after_sunrise_to_full_brightness = settings_file.hours_after_sunrise_to_full_brightness
        self.hours_before_sunset_to_start_dimmer = settings_file.hours_before_sunset_to_start_dimmer

        if api_weather_details:
            ## See https://github.com/csparpa/pyowm/blob/master/pyowm/docs/usage-examples.md for pyowm details
            ##
            ## For future weather alerts
            ## weather_condition = w.get_detailed_status()
            
            self.weather_condition = api_weather_details.get_status()
            
            ## Get temperature data
            temperature_data = api_weather_details.get_temperature("fahrenheit")
            self.min_temperature = int(temperature_data["temp_min"])
            self.max_temperature = int(temperature_data["temp_max"])
            self.current_temperature = int(temperature_data["temp"])
            
            ## Get sunrise hour and minute
            sunrise_time = api_weather_details.get_sunrise_time()
            self.sunrise_hour = self.getUsableTime(sunrise_time, '%H')
            self.sunrise_minute = self.getUsableTime(sunrise_time, '%M')
            
            ## Get sunset hour and minute
            sunset_time = api_weather_details.get_sunset_time()
            self.sunset_hour = self.getUsableTime(sunset_time, '%H')
            self.sunset_minute = self.getUsableTime(sunset_time, '%M')

            self.good_weather_fetch = True

        else:
            self.weather_condition = "N/A"
            self.current_temperature = 0
            self.sunrise_hour = settings_file.default_sunrise_hour
            self.sunrise_minute = settings_file.default_sunrise_minute
            self.sunset_hour = settings_file.default_sunset_hour
            self.sunset_minute = settings_file.default_sunset_minute
            
            self.good_weather_fetch = False
            
    def getUsableTime(self, time, unit):
        usable_time = datetime.datetime.fromtimestamp(int(time)).strftime(unit)
        return int(usable_time)

def getWeatherData(call_api=True):
    if call_api:
        try:
            ## Call the API
            weather_details = owm.weather_at_coords(lat, lon)
            weather = Weather(weather_details.get_weather())
     
        except:
            weather = Weather()
    else:
        weather = Weather()

    return weather

