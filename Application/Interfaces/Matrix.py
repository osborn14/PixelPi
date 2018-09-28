import os, math, time, datetime, calendar

import Application.Keys.Settings as SETTINGS
from Application.Interfaces.Interface import Interface
from Application.Interfaces.Common.Weather import Weather, getWeatherData
from Application.Interfaces.Common.Animation import Animation
import Application.Interfaces.Common.RPiClockFunctions as clock_fx
import Application.Interfaces.Common.RPiLEDFunctions as led_fx
from Application.Interfaces.MatrixDisplayModes import Flat#, Rainbow, Gradient, Singles

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

class Matrix(Interface):
    def __init__(self, settings):
        super().__init__(settings)
        
        self.chain_length = 2
        self.matrix_width = 32 * self.chain_length
        self.matrix_height = 32

        # Configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.chain_length = self.chain_length
        options.parallel = 1
        options.disable_hardware_pulsing = True
        options.hardware_mapping = 'adafruit-hat' if settings[SETTINGS.HAT] else 'regular'
        
        print("Before creating matrix")
        self.matrix = RGBMatrix(options = options)
        print("After creating matrix")
        
        self.font = graphics.Font().LoadFont(os.path.dirname(os.path.abspath(__file__)) + "/fonts/7x13B.bdf")
        self.font_small = graphics.Font().LoadFont(os.path.dirname(os.path.abspath(__file__)) + "/fonts/6x10.bdf")

        os.environ['TZ'] = settings[SETTINGS.TIME_ZONE]
        self.military_time_bool = settings[SETTINGS.MILITARY_TIME]

        self.adjusted_main_height_list = [1] * 16
        self.adjusted_tip_height_list = [2] * 16

        self.fetch_weather_time = time.time()
        self.weather_data = getWeatherData()
        self.colon_counter = 0
        self.first_time = True
        self.refresh_pause = .5
        self.dimmer_minimum = 0.02
        
        print("End settings")

    def getAdjustedSpectrumHeightList(self, prev_main_height_list, new_spectrum_height_list):
        for i in range(len(prev_main_height_list)):
            prev_main_height_list[i] = prev_main_height_list[i] - 3 if prev_main_height_list[i] - 3 > new_spectrum_height_list[i] else new_spectrum_height_list[i]

        return prev_main_height_list

    def getAdjustedSpectrumTipHeightList(self, adjusted_main_height_list, adjusted_tip_height_list):
        for i in range(len(adjusted_tip_height_list)):
            if adjusted_main_height_list[i] == 0 and adjusted_tip_height_list[i] == 1:
                adjusted_tip_height_list[i] = 0
            elif adjusted_main_height_list[i] < adjusted_tip_height_list[i] - 1:
                adjusted_tip_height_list[i] = adjusted_tip_height_list[i] - 1
            else:
                adjusted_tip_height_list[i] = adjusted_main_height_list[i] + 1

        return adjusted_tip_height_list


    def displayAudioLights(self, audio_data):
        # if audio_data.display_mode == 3:
        #     dm3 = DisplayModeThree(main_height, tip_height, LED_MATRIX_WIDTH, total_bars)
        #     lower_main_rgb = audio_data.server_secondary_colors
        # else:
        #     lower_main_rgb = [255, 255, 255]
        
        print("in display audio")
        
        display_mode_dict = {
            0: Flat,
            1: Rainbow,
            2: Gradient,
            3: Singles
        }

        #display_mode = display_mode_dict[audio_data.display_mode]()
        display_mode = display_mode_dict[0](audio_data)

        self.adjusted_main_height_list = self.getAdjustedSpectrumHeightList(self.adjusted_main_height_list, audio_data.spectrum_heights)
        self.adjusted_tip_height_list = self.getAdjustedSpectrumTipHeightList(self.adjusted_main_height_list, self.adjusted_tip_height_list)
        
        print("Before getting frame")
        offscreen_canvas = display_mode.getFrame(self.adjusted_main_height_list, self.adjusted_tip_height_list)

        # y_height_list = display_mode.calculateHeightList(self.adjusted_main_height_list, self.matrix_width)
        # tip_height_list = display_mode.calculateTipHeightList(y_height_list, self.adjusted_tip_height_list)
        #
        #
        # for x in range(self.matrix_width):
        #     display_mode.setX(x)
        #
        #     for y in range(len(y_height_list)):
        #         display_mode.getColor(x)
        #         main_rgb = led_fx.getFadedColors(y_height_list[x], y, audio_data.server_primary_colors)
        #
        #         self.matrix.SetPixel(x, 32 - y, main_rgb[0], main_rgb[1], main_rgb[2])
        #
        #     tip_rgb = display_mode.getTipColor(audio_data.server_primary_colors, audio_data.server_secondary_colors)
        #     self.matrix.SetPixel(x, 32 - tip_height_list[x], tip_rgb[0], tip_rgb[1], tip_rgb[2])
        #

        self.matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(.05)





        ## For each bar displayed
        # for bar_i in range(len(self.main_height)):
        #     main_rgb = audio_data.server_primary_colors
        #     tip_rgb = audio_data.server_secondary_colors
        #     ## Get the upper transition value for the bar.  This will come in handy for fading the column, when we get to that
        #     uppertransitionrange = 0
        #
        #     main_rgb = led_fx.applyGradientEffects(main_rgb, tip_rgb, audio_data.display_mode, bar_i)
        #
        #     ## Set the height of the tip we want to display.  We don't want to simply display the tip at the top of the bar
        #     ## because the tip should fall down slower than the bar itself
        #     tip_height[bar_i] = led_fx.calculateBarHeight(self.main_height, tip_height, bar_i)
        #
        #     x_columns_per_bar = getXColumnsPerBar(audio_data.display_mode, LED_MATRIX_WIDTH, total_bars, bar_width)
        #
        #     ## MAKE DISPLAY MODE 1 ON ADRESSABBLW BE TEMP_ RGB AT 0
        #     ## PUT THE BAR SETS IN ORDER. FIND A QUARTER OF THE SETS, THEN if i < 4 - 1 AND i > 0 + 1
        #
        #     for single_column_in_bar_i in range(0, x_columns_per_bar):
        #         x = getX(audio_data.display_mode, bar_i, single_column_in_bar_i)
        #
        #         ## Can't simply wipe the screen.  It makes the animation look choppy
        #         for clear_i in range(0, 32):
        #             matrix.SetPixel(x, clear_i, 0, 0, 0)
        #
        #         temp_main_height = getMainHeight(dm3, self.main_height, single_column_in_bar_i)
        #         temp_tip_height = getTipHeight(dm3, self.tip_height, single_column_in_bar_i)
        #
        #         line_height = temp_main_height[bar_i] + 1
        #
        #         if temp_main_height[bar_i] >= FADE_START:
        #             uppertransitionrange = temp_main_height[bar_i] - FADE_START
        #
        #             ## Draw the vertical line corresponing to each x point
        #         for drawline in range(1, line_height):
        #             temp_rgb = led_fx.getFadedColors(FADE_START, FADE_END, uppertransitionrange,
        #                                              temp_main_height[bar_i], drawline, main_rgb, lower_main_rgb)
        #             matrix.SetPixel(x, 32 - drawline, temp_rgb[0], temp_rgb[1], temp_rgb[2])
        #
        #         ## Get the final tip color
        #         tip_rgb = led_fx.getTipColor(DisplayMode, main_rgb, tip_rgb)
        #
        #         ## Set the tip pixel on top of the chart
        #         ## "32 -" makes the spectrum analyzer display right side up
        #         matrix.SetPixel(x, 32 - temp_tip_height[bar_i], tip_rgb[0], tip_rgb[1], tip_rgb[2])
        #
        # self.offset_canvas = self.matrix.SwapOnVSync(matrix)
        # time.sleep(PAUSE_TIME)

    def displayNormalLights(self):
        print("In displayNormalLights")
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        print("After creating offscreen canvas")

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

        dimmer = clock_fx.calculateDimmer(current_hour, current_minute, self.weather_data.sunrise_hour,
                                          self.weather_data.sunrise_minute,
                                          self.weather_data.hours_after_sunrise_to_full_brightness, self.weather_data.sunset_hour,
                                          self.weather_data.sunset_minute, self.weather_data.hours_before_sunset_to_start_dimmer,
                                          self.dimmer_minimum)
        isDay = clock_fx.getIsDay(dimmer, self.dimmer_minimum)

        ################ TESTING VARIABLES ###################
        isDay = isDay
        weather_condition = self.weather_data.weather_condition
        ####################### END ##########################

        animation_to_draw = []
        animation = Animation(51, 2)
        color_scheme = clock_fx.getColorScheme(weather_condition, dimmer, isDay)
        MAIN_COLOR = color_scheme[0]
        SUB_COLOR = color_scheme[1]
        
        print("here 10")

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

        #offscreen_canvas.Clear()
        
        print("Here 11")

        for i in range(len(animation_to_draw)):
            pixel = animation_to_draw[i]
            offscreen_canvas.SetPixel(pixel.x, pixel.y, pixel.rgb[0], pixel.rgb[1], pixel.rgb[2])
            
        print("here 12")
        #graphics.DrawText(offscreen_canvas, self.font, 0, 22, SUB_COLOR, todays_date)
        #graphics.DrawText(offscreen_canvas, self.font, 0, 10, MAIN_COLOR, current_time_str)
        print("here 13")
        ##            if weather_data.good_weather_fetch:
        static_text = str(weather_data.current_temperature) + "F " + weather_data.weather_condition
        #graphics.DrawText(offscreen_canvas, self.font_small, 0, 31, MAIN_COLOR, static_text)
        
        print("Before swap")
        
        self.matrix.SwapOnVSync(offscreen_canvas)
        time.sleep(self.refresh_pause)


        