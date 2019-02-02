from rgbmatrix import graphics

def getColonorSpace(refresh_pause, colon_counter):
    if colon_counter < 1 / refresh_pause:
        colon_or_space = ":"
    elif colon_counter < 2 / refresh_pause:
        colon_or_space = " "
    else:
        colon_or_space = ":"

    return colon_or_space

def getColorScheme(weather_condition, dimmer, isDay):
    ## Set some predefined colors
    WHITE = graphics.Color(245 * dimmer, 245 * dimmer, 245 * dimmer)
    NIGHT_WHITE = graphics.Color(5, 5, 5)
    GREY = graphics.Color(128 * dimmer, 128 * dimmer, 128 * dimmer)
    NIGHT_GREY = graphics.Color(2, 2, 2)
    GOLD = graphics.Color(255 * dimmer, 215 * dimmer, 0)
    ORANGE = graphics.Color(255 * dimmer, 165 * dimmer, 0)
    RED = graphics.Color(255 * dimmer, 0, 0)
    BLUE = graphics.Color(0, 0, 255 * dimmer)
    LIGHT_BLUE = graphics.Color(25 * dimmer, 25 * dimmer, 128 * dimmer)
    DARK_BLUE = graphics.Color(0, 0, 128 * dimmer)
    NIGHT_DARK_BLUE = graphics.Color(0, 0, 2)
    GREEN = graphics.Color(0, 255 * dimmer, 0)

    if weather_condition == "Clear":
        if isDay:
            MAIN_COLOR = GOLD
            SUB_COLOR = LIGHT_BLUE
        else:
            MAIN_COLOR = NIGHT_WHITE
            SUB_COLOR = NIGHT_GREY
    elif weather_condition == "Clouds":
        if isDay:
            MAIN_COLOR = WHITE
            SUB_COLOR = GREY
        else:
            MAIN_COLOR = NIGHT_WHITE
            SUB_COLOR = NIGHT_GREY
    elif weather_condition == "Rain":
        if isDay:
            MAIN_COLOR = GREY
            SUB_COLOR = DARK_BLUE
        else:
            MAIN_COLOR = NIGHT_GREY
            SUB_COLOR = NIGHT_DARK_BLUE
    elif weather_condition == "Thunderstorm":
        if isDay:
            MAIN_COLOR = GREY
            SUB_COLOR = DARK_BLUE
        else:
            MAIN_COLOR = NIGHT_GREY
            SUB_COLOR = NIGHT_DARK_BLUE
    else:
        if isDay:
            MAIN_COLOR = WHITE
            SUB_COLOR = GREY
        else:
            MAIN_COLOR = NIGHT_WHITE
            SUB_COLOR = NIGHT_GREY

    return [MAIN_COLOR, SUB_COLOR]

def getTimeCounter(avg, no_display_tolerance, music_detected_counter):
    if avg > no_display_tolerance:
        music_detected_counter = music_detected_counter + 1
    else:
        music_detected_counter = 0

    return music_detected_counter

def AMorPM(current_hour, military_time_bool):
    if military_time_bool:
        am_or_pm = ""
    else:
        am_or_pm = "am"
        if current_hour > 11:
            am_or_pm = "pm"
            
    return am_or_pm

def calculateDimmer(current_hour, current_minute, weather_data, dimmer_minimum = 0.02):
    time_till_sunrise_is_over = 60 * (weather_data.sunrise_hour + weather_data.hours_after_sunrise_to_full_brightness - current_hour) + (weather_data.sunrise_minute - current_minute)
    time_till_sunset = 60 * (weather_data.sunset_hour - current_hour) + (weather_data.sunset_minute - current_minute)
    
    if 0 <= time_till_sunrise_is_over < 60 * weather_data.hours_after_sunrise_to_full_brightness:
        dimmer = time_till_sunrise_is_over / (60 * weather_data.hours_after_sunrise_to_full_brightness) + dimmer_minimum
    elif 0 <= time_till_sunset < 60 * weather_data.hours_before_sunset_to_start_dimmer:
        dimmer = time_till_sunset / (60 * weather_data.hours_before_sunset_to_start_dimmer) + dimmer_minimum
    elif 0 < time_till_sunrise_is_over or time_till_sunset < 0:
        dimmer = dimmer_minimum
    else:
        dimmer = 1

    if 1 < dimmer:
        dimmer = 1

    return dimmer

def getIsDay(dimmer, dimmer_minimum):
    isDay = False
    if dimmer > dimmer_minimum:
        isDay = True

    return isDay

def getCurrentHour(current_hour, military_time_bool):
    if not military_time_bool:
        if current_hour > 12:
            current_hour = current_hour - 12
        elif current_hour == 0:
            current_hour = 12
    
    return current_hour
