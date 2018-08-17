import os, time, datetime

from Application.Interfaces.SharedFunctions.Weather import Weather, getWeatherData
from Application.Interfaces.SharedFunctions.Animation import Animation
from Application.Interfaces.SharedFunctions.RPiClockFunctions as clock_fx

from samplebase import SampleBase
from rgbmatrix import RGBMatrix, graphics, RGBMatrixOptions

class MatrixRunner(SampleBase):
    def __init__(self, matrix_settings):
        # TODO: Pass in valid arguments
        super(MatrixRunner, self).__init__(*args, **kwargs)
        
        os.environ['TZ'] = settings_file.time_zone

        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont("/home/pi/Documents/rpi-rgb-led-matrix-master/fonts/7x13B.bdf")
        self.font_small = graphics.Font()
        self.font_small.LoadFont("/home/pi/Documents/rpi-rgb-led-matrix-master/fonts/6x10.bdf")

        os.environ['TZ'] = matrix_settings.time_zone

        self.military_time_bool = matrix_settings.self.military_time_bool

        self.fetch_weather_time = time.time()
        self.colon_counter = 0
        self.first_time = True
        self.refresh_pause = .5
        self.dimmer_minimum = 0.02
        
    def displayDefault(self):
        if time.time() - self.fetch_weather_time >= 1800 or self.first_time == True:
            self.fetch_weather_time = time.time()
            weather_data = getWeatherData()

            self.first_time = False

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

        dimmer = clock_fx.calculateDimmer(current_hour, current_minute, weather_data.sunrise_hour,
                                          weather_data.sunrise_minute,
                                          weather_data.hours_after_sunrise_to_full_brightness, weather_data.sunset_hour,
                                          weather_data.sunset_minute, weather_data.hours_before_sunset_to_start_dimmer,
                                          self.dimmer_minimum)
        isDay = clock_fx.getIsDay(dimmer, self.dimmer_minimum)

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

        colon_or_space = clock_fx.getColonorSpace(self.refresh_pause, self.colon_counter)
        self.colon_counter = self.colon_counter + 1 if self.colon_counter < 2 else 0

        am_or_pm = clock_fx.AMorPM(current_hour, self.military_time_bool)
        current_hour = clock_fx.getCurrentHour(current_hour, self.military_time_bool)

        current_hour_str = str(current_hour)
        current_minute_str = str(current_minute)

        if len(current_hour_str) == 1:
            current_hour_str = "0" + current_hour_str

        if len(current_minute_str) == 1:
            current_minute_str = "0" + current_minute_str

        current_time_str = current_hour_str + colon_or_space + current_minute_str + am_or_pm

        self.offscreen_canvas.Clear()

        for i in range(len(animation_to_draw)):
            pixel = animation_to_draw[i]
            self.offscreen_canvas.SetPixel(pixel.x, pixel.y, pixel.rgb[0], pixel.rgb[1], pixel.rgb[2])

        graphics.DrawText(self.offscreen_canvas, self.font, 0, 22, SUB_COLOR, todays_date)
        graphics.DrawText(self.offscreen_canvas, self.font, 0, 10, MAIN_COLOR, current_time_str)

        ##            if weather_data.good_weather_fetch:
        static_text = str(weather_data.current_temperature) + "F " + weather_data.weather_condition
        graphics.DrawText(self.offscreen_canvas, self.font_small, 0, 31, MAIN_COLOR, static_text)

        self.matrix.SwapOnVSync(self.offscreen_canvas)
        time.sleep(self.refresh_pause)

    def displayAudioLights(self):


    def displayLights(self):
        