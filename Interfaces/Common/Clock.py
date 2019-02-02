import sys, datetime, calendar

import Keys.Settings as SETTINGS


class Clock:
    def __init__(self, settings):
        self.settings = settings
        self.military_time_bool = settings[SETTINGS.MILITARY_TIME]
        self.color_scheme_dict = {
            SETTINGS.WHITE: [245, 245, 245],
            SETTINGS.NIGHT_WHITE: [5, 5, 5],
            SETTINGS.GREY: [128, 128, 128],
            SETTINGS.NIGHT_GREY: [2, 2, 2],
            SETTINGS.GOLD: [255, 215, 0],
            SETTINGS.ORANGE: [255, 165, 0],
            SETTINGS.RED: [255, 0, 0],
            SETTINGS.BLUE: [0, 0, 255],
            SETTINGS.LIGHT_BLUE: [25, 25, 128],
            SETTINGS.DARK_BLUE: [0, 0, 128],
            SETTINGS.NIGHT_DARK_BLUE: [0, 0, 2],
            SETTINGS.GREEN: [0, 255, 0]
        }

        self.colon_counter = 0
        self.refresh_pause = 0.5
        
    def setMainAndSubColor(self, weather_condition, is_day):
        if weather_condition == SETTINGS.CLEAR:
            if is_day:
                self.main_color = self.color_scheme_dict[SETTINGS.GOLD]
                self.sub_color = self.color_scheme_dict[SETTINGS.LIGHT_BLUE]
            else:
                self.main_color = self.color_scheme_dict[SETTINGS.NIGHT_WHITE]
                self.sub_color = self.color_scheme_dict[SETTINGS.NIGHT_GREY]

        elif weather_condition == SETTINGS.CLOUDS:
            if is_day:
                self.main_color = self.color_scheme_dict[SETTINGS.WHITE]
                self.sub_color = self.color_scheme_dict[SETTINGS.GREY]
            else:
                self.main_color = self.color_scheme_dict[SETTINGS.NIGHT_WHITE]
                self.sub_color = self.color_scheme_dict[SETTINGS.NIGHT_GREY]

        elif weather_condition == SETTINGS.RAIN:
            if is_day:
                self.main_color = self.color_scheme_dict[SETTINGS.GREY]
                self.sub_color = self.color_scheme_dict[SETTINGS.DARK_BLUE]
            else:
                self.main_color = self.color_scheme_dict[SETTINGS.NIGHT_GREY]
                self.sub_color = self.color_scheme_dict[SETTINGS.NIGHT_DARK_BLUE]

        elif weather_condition == SETTINGS.THUNDERSTORM:
            if is_day:
                self.main_color = self.color_scheme_dict[SETTINGS.GREY]
                self.sub_color = self.color_scheme_dict[SETTINGS.DARK_BLUE]
            else:
                self.main_color = self.color_scheme_dict[SETTINGS.NIGHT_GREY]
                self.sub_color = self.color_scheme_dict[SETTINGS.NIGHT_DARK_BLUE]

        else:
            if is_day:
                self.main_color = self.color_scheme_dict[SETTINGS.WHITE]
                self.sub_color = self.color_scheme_dict[SETTINGS.GREY]
            else:
                self.main_color = self.color_scheme_dict[SETTINGS.NIGHT_WHITE]
                self.sub_color = self.color_scheme_dict[SETTINGS.NIGHT_GREY]

    def updateTime(self):
        current_datetime = datetime.datetime.now()
        current_hour = int(current_datetime.hour)
        current_minute = int(current_datetime.minute)

        current_month = str(current_datetime.month)
        current_day = str(current_datetime.day)

        current_date = datetime.date.today()
        day_of_the_week = calendar.day_name[current_date.weekday()]

        day_of_the_week_abbreviation = day_of_the_week[:3]
        todays_date = day_of_the_week_abbreviation + " " + current_month + "/" + current_day

    def getMatrixColorScheme(self, weather_condition, dimmer, is_day):
        if 'graphics' not in sys.modules:
            from rgbmatrix import graphics

        self.setMainAndSubColor(weather_condition, is_day)

        adjusted_main_color = list(map(lambda color: color * dimmer, self.main_color))
        adjusted_sub_color = list(map(lambda color: color * dimmer, self.sub_color))

        graphics_main_color = graphics.Color(adjusted_main_color[0], adjusted_main_color[1], adjusted_main_color[2])
        graphics_sub_color = graphics.Color(adjusted_sub_color[0], adjusted_sub_color[1], adjusted_sub_color[2])

        return [graphics_main_color, graphics_sub_color]

    def getColonorSpace(self):
        if self.colon_counter < 1 / self.refresh_pause:
            colon_or_space = ":"
        elif self.colon_counter < 2 / self.refresh_pause:
            colon_or_space = " "
        else:
            colon_or_space = ":"

        self.colon_counter = self.colon_counter + 1 if self.colon_counter < 2 else 0

        return colon_or_space

    def getAMorPM(self, current_hour):
        if self.military_time_bool:
            am_or_pm = ""
        else:
            if current_hour <= 11:
                am_or_pm = SETTINGS.AM
            else:
                am_or_pm = SETTINGS.PM

        return am_or_pm

    def calculateDimmer(self, current_hour, current_minute, weather_data, dimmer_minimum=0.02):
        time_till_sunrise_is_over = 60 * (
                weather_data.sunrise_hour + weather_data.hours_after_sunrise_to_full_brightness - current_hour) + (
                                            weather_data.sunrise_minute - current_minute)
        time_till_sunset = 60 * (weather_data.sunset_hour - current_hour) + (
                    weather_data.sunset_minute - current_minute)

        if 0 <= time_till_sunrise_is_over < 60 * weather_data.hours_after_sunrise_to_full_brightness:
            dimmer = time_till_sunrise_is_over / (
                        60 * weather_data.hours_after_sunrise_to_full_brightness) + dimmer_minimum
        elif 0 <= time_till_sunset < 60 * weather_data.hours_before_sunset_to_start_dimmer:
            dimmer = time_till_sunset / (60 * weather_data.hours_before_sunset_to_start_dimmer) + dimmer_minimum
        elif 0 < time_till_sunrise_is_over or time_till_sunset < 0:
            dimmer = dimmer_minimum
        else:
            dimmer = 1

        if 1 < dimmer:
            dimmer = 1

        return dimmer

    def getFormattedTime(self):
        pass


def getIsDay(dimmer, dimmer_minimum):
    is_day = False
    if dimmer > dimmer_minimum:
        is_day = True

    return is_day


def getCurrentHour(current_hour, military_time_bool):
    if not military_time_bool:
        if current_hour > 12:
            current_hour = current_hour - 12
        elif current_hour == 0:
            current_hour = 12

    return current_hour
