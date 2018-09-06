import time
import Application.Keys.Settings as SETTINGS
from Application.Interfaces.Interface import Interface
from Application.Interfaces.Common import RPiLEDFunctions as led_fx
from neopixel import *

class Neopixel(Interface):
    def __init__(self, settings):
        super().__init__(settings)

        # LED strip configuration:
        self.LED_COUNT                          = settings[SETTINGS.LED_COUNT]      # Number of LED pixels.
        LED_PIN                                 = settings[SETTINGS.MAIN_PIN]      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ                             = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA                                 = 10       # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS                          = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT                              = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL                             = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        # Defining some settings
        self.LED_DIMMER                         = 0.75
        self.PAUSE_TIME                         = 1 / 20
        # self.BAR_RANGE                          = float(self.LED_COUNT / 16)
        self.BAR_RANGE = self.LED_COUNT / 16

        rgb_order_dict = {
            SETTINGS.RED: 0,
            SETTINGS.GREEN: 1,
            SETTINGS.BLUE: 2
        }
        self.rgb_order = list(map(lambda rgb: rgb_order_dict[rgb], settings[SETTINGS.RGB_ORDER]))

        self.timer_tasks = list()
        self.main_height = [0] * 16

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    def displayAudioLights(self, audio_data):
        #print("audio data from server", audio_data.spectrum_heights)
        #print("self.main_height      ", self.main_height)
        
        self.main_height = led_fx.getDataListtoPrint(self.main_height, audio_data.spectrum_heights)
        
        if audio_data.display_mode == 2 or audio_data.display_mode == 3:
            lower_main_rgb = audio_data.server_secondary_colors
        else:
            lower_main_rgb = self.blendColors(audio_data.server_primary_colors, [255, 255, 255])
        
        lower_main_rgb = [0, 0, 0]
        
        display_rgb = [0] * 3

        for bar_i in range(len(self.main_height)):
            for i in range(len(audio_data.server_primary_colors)):
                display_rgb[i] = int(audio_data.server_primary_colors[i] * self.main_height[bar_i] / 32)
            
            starting_x = int(bar_i * self.BAR_RANGE)
            ending_x = int((bar_i + 1) * self.BAR_RANGE)
                        
            for individual_pixel in range(starting_x, ending_x):
                display_color = Color(display_rgb[0], display_rgb[1], display_rgb[2])
                self.strip.setPixelColor(individual_pixel, display_color)

        self.strip.show()
        time.sleep(self.PAUSE_TIME)

    def displayNormalLights(self):
        rgb_to_display = self.getRgbToDisplay()
        
        # Our display loops will expect an array of arrays, so make sure that's always the case
        if not isinstance(rgb_to_display[0], list):
            rgb_to_display = [rgb_to_display]            
        
        x = 0
        while x <= self.LED_COUNT:
            for rgb in rgb_to_display:
                display_color = Color(rgb[0], rgb[1], rgb[2])
                self.strip.setPixelColor(x, display_color)
                x+=1

        # Display strip
        self.strip.show()


    def displayDefaultLights(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        time.sleep(self.PAUSE_TIME * 5)
        
    def blendColors(self, main_rgb, tip_rgb):
        blended_rgb = [0] * 3
        for i in range(len(main_rgb)):
            blended_rgb[i] = (main_rgb[i] + tip_rgb[i])/2.0

        return blended_rgb  
