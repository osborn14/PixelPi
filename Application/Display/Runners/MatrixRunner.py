import time, datetime

class MatrixRunner():
    def __init__(self):

    def displayAudioLights(self):


    def displayLights(self):
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

        dimmer = clock_fx.calculateDimmer(current_hour, current_minute, weather_data.sunrise_hour,
                                          weather_data.sunrise_minute,
                                          weather_data.hours_after_sunrise_to_full_brightness, weather_data.sunset_hour,
                                          weather_data.sunset_minute, weather_data.hours_before_sunset_to_start_dimmer,
                                          dimmer_minimum)
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
        time.sleep(refresh_pause)