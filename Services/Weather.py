import pyowm, time, datetime

import Keys.Settings as SETTINGS
import Keys.Network as NETWORK

from Services.Service import Service


class Weather(Service):
    def __init__(self, settings):
        super().__init__(settings)

        print(settings)

        self.api_key = self.settings[SETTINGS.PYOWM_API_KEY]
        self.latitude = self.settings[SETTINGS.LATITUDE]
        self.longitude = self.settings[SETTINGS.LONGITUDE]
        self.open_weather_map_object = pyowm.OWM(self.api_key)

        self.hours_after_sunrise_to_full_brightness = 3
        self.hours_before_sunset_to_start_dimmer = 3
        self.fetch_weather_time = 0

    def update(self):
        if time.time() - self.fetch_weather_time >= 1800:
            self.fetch_weather_time = time.time()
            self.weather_data.updateWeatherData()

        self.weather_details = self.open_weather_map_object.weather_at_coords(self.latitude, self.longitude)
        api_weather_details = Weather(self.weather_details.get_weather())

        # api_weather_details = None
        if api_weather_details:
            ## See https://github.com/csparpa/pyowm/blob/master/pyowm/docs/usage-examples.md for pyowm details
            ##
            ## For future weather alerts
            ## weather_condition = w.get_detailed_status()

            self.weather_condition = api_weather_details.get_status()

            # Get temperature data
            temperature_data = api_weather_details.get_temperature("fahrenheit")
            self.min_temperature = int(temperature_data["temp_min"])
            self.max_temperature = int(temperature_data["temp_max"])
            self.current_temperature = int(temperature_data["temp"])

            # Get sunrise hour and minute
            sunrise_time = api_weather_details.get_sunrise_time()
            self.sunrise_hour = self.getUsableTime(sunrise_time, '%H')
            self.sunrise_minute = self.getUsableTime(sunrise_time, '%M')

            # Get sunset hour and minute
            sunset_time = api_weather_details.get_sunset_time()
            self.sunset_hour = self.getUsableTime(sunset_time, '%H')
            self.sunset_minute = self.getUsableTime(sunset_time, '%M')

            self.good_weather_fetch = True

        else:
            self.weather_condition = "N/A"
            self.current_temperature = 0
            # self.sunrise_hour = settings_file.default_sunrise_hour
            # self.sunrise_minute = settings_file.default_sunrise_minute
            # self.sunset_hour = settings_file.default_sunset_hour
            # self.sunset_minute = settings_file.default_sunset_minute

            self.sunrise_hour = 7
            self.sunrise_minute = 30
            self.sunset_hour = 20
            self.sunset_minute = 0

            self.good_weather_fetch = False

            return self.good_weather_fetch

    def getBroadcastDict(self, audio_data):
        broadcast_dict = {
            NETWORK.COMMAND: NETWORK.UPDATE,
            SETTINGS.SERVICE: SETTINGS.WEATHER,
            SETTINGS.WEATHER_CONDITION: self.weather_condition,
            SETTINGS.CURRENT_TEMPERATURE: self.current_temperature,
            SETTINGS.SUNRISE_HOUR: self.sunrise_hour,
            SETTINGS.SUNRISE_MINUTE: self.sunrise_minute,
            SETTINGS.SUNSET_HOUR: self.sunset_hour,
            SETTINGS.SUNSET_MINUTE: self.sunset_minute,
            SETTINGS.GOOD_WEATHER_FETCH: self.good_weather_fetch
        }

        return broadcast_dict

    def getUsableTime(self, time, unit):
        usable_time = datetime.datetime.fromtimestamp(int(time)).strftime(unit)
        return int(usable_time)
