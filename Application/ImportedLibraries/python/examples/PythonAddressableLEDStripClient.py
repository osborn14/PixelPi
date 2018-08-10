
import sys, os, threading, time, datetime, subprocess, signal, socket, random
import RPiLEDFunctions as led_fx
from Settings import Settings
from neopixel import *

## Get our settings object that includes any user defined settings
settings_file = Settings()

# LED strip configuration:
LED_COUNT      = settings_file.led_count      # Number of LED pixels.
LED_PIN        = settings_file.strip_led_addressable_pin      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


class Pulse(object):
    def __init__(self, mm, m):
        self.x_location = 0.0
        self.max_magnitude = mm
        self.magnitude = m
        self.tail = int(2 * m)
        
    def moveRight(self):
        self.x_location = self.x_location + 1

    def getDisplayColor(self, main_rgb, secondary_rgb, tail_i = 0):
        ## Secondary rgb will be the color of the pulse, while main rgb is the existing color on the strip
        pulse_rgb = [0, 0, 0]
        difference_between_arrays = [0, 0, 0]
        magnitude_fraction = self.magnitude / (self.max_magnitude * 1.0)
        tail_fraction = (self.tail - tail_i) /  (self.tail * 1.0)

        for i in range(len(pulse_rgb)):
            difference_between_arrays[i] = secondary_rgb[i] - main_rgb[i]
            secondary_color_value = difference_between_arrays[i] * magnitude_fraction * tail_fraction
            pulse_rgb[i] = main_rgb[i] + secondary_color_value

        return pulse_rgb

def drawList(strip, print_list):
    for i in range(len(print_list)):
        display_rgb = print_list[i]
        display_color = Color(int(display_rgb[0]), int(display_rgb[1]), int(display_rgb[2]))
        strip.setPixelColor(i, display_color)

    return strip

def removeAnyOldPulses(pulse_list):
    if len(pulse_list) > 0:
        pulse_to_maybe_delete = pulse_list[-1]
        
        if pulse_to_maybe_delete.x_location >= led_strip_length:
            pulse_list.remove(pulse_to_maybe_delete)

    return pulse_list

def turnOffLights(strip, led_strip_length):
    for i in range(led_strip_length):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

    return True


def spectrumPulse(strip):
    ## The first server provides us with the audio spectrum analysis, broken into 16 pieces
    sock1 = socket.socket()
    sock1.connect((settings_file.ServerIP, 8080))
    
    ## The second server will give us all the main and secondary rgb information, along with display mode
    sock2 = socket.socket()
    sock2.connect((settings_file.ServerIP, 8081))

    ## lastdisplayedvalue makes sure we don't display any values that are older than what we just displayed
    ## only new values should be displayed
    lastdisplayedvalue = 0

    main_height = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    bass_list = [0, 0, 0]
    bass_list_len = len(bass_list)
    pulse_list = []

    lower_main_rgb = [255, 255, 255]
    
    main_rgb = [0, 0, 0]
    tip_rgb = [0, 0, 0]

    start_time = time.time()

    strip_led_brightness = 0
    turned_off = Fslse
    
    ## Gets settings from settings_file object
    PIN_Array_Main = [settings_file.main_red_pin, settings_file.main_green_pin, settings_file.main_blue_pin]
    PIN_Array_Secondary = [settings_file.tip_red_pin, settings_file.tip_green_pin, settings_file.tip_blue_pin]
    strip_led_brightness_multiplier = settings_file.led_brightness_multiplier
    pause_time = 1 / settings_file.target_fps
    led_strip_length = LED_COUNT
    pulse_max_magnitude = 3
    
    while True:
        ## Get the values from the first server
        expected_array_list_size1 = 19
        rawdata1 = sock1.recv(4096)
        datalist1 = led_fx.returnUsableServerData(rawdata1, expected_array_list_size1)

        if datalist1[0] > lastdisplayedvalue:
            lastdisplayedvalue = datalist1[0]
            ## Get the values from the second server
            expected_array_list_size2 = 7
            rawdata2 = sock2.recv(4096)
            datalist2 = led_fx.returnUsableServerData(rawdata2, expected_array_list_size2)
            
            DisplayMode = datalist2[0]
            main_rgb = [datalist2[1], datalist2[2], datalist2[3]]
            if DisplayMode == 2:
                tip_rgb = [255, 255, 255]
            else:
                tip_rgb = [datalist2[4], datalist2[5], datalist2[6]]

            avg = led_fx.getAverageofListValues(datalist1, 1, 17)
            
            recent_bass_avg = led_fx.getAverageofListValues(bass_list, 0, bass_list_len)
            new_bass_avg = led_fx.getAverageofListValues(datalist1, 1, 3)

            print(new_bass_avg, " --- ", recent_bass_avg)

            for i in range(bass_list_len):
                bass_list[i] = new_bass_avg

            bass_difference = new_bass_avg - recent_bass_avg
            
            if bass_difference >= 2:
                bass_difference = bass_difference if bass_difference < 3 else 3
                p = Pulse(pulse_max_magnitude * 1.0, bass_difference / 2.0)
                pulse_list.insert(0, p)

            bass_list.insert(0, new_bass_avg)
            bass_list.pop(bass_list_len)
            
            main_height = led_fx.getDataListtoPrint(main_height, datalist1, 1, 17)
            
            if avg < settings_file.no_display_tolerance:
                for i in range(1,17):
                    ## Remove any small static that the server sends over
                    main_height[i] = 1
                    
                if time.time() - start_time > 60:
                    ## Has it been 60 seconds with no activity?  If so, close the program
                    if not turned_off:
                        turned_off = turnOffLights(strip, led_strip_length, turned_off)
                    
                    time.sleep(pause_time * 5)
                    continue;

            else:
                start_time = time.time()
                turned_off = False

            if DisplayMode == 0 or DisplayMode == 2 or DisplayMode == 3:
                ## Strip brightness is the actual number (between 0 and 1) that determines the intensity of the displayed color
                strip_led_brightness = led_fx.calculateStripLEDBrightness(strip_led_brightness * 1.0, avg * 1.0)

                ## Temp strip brightness takes the strip brightness and multiplies it by a certain factor, so the displayed color is brighter
                ## at lower noise volumes
                temp_strip_led_brightness = led_fx.calculateTempStripLEDBrightness(strip_led_brightness * 1.0, strip_led_brightness_multiplier * 1.0, 25)

                ## Reduces the green in the output to the pins.
                ## For my own strip lights, unmodified outputs makes the oranges look too greenish
                temp_led_strip_color_main = led_fx.getMainLEDStripValuestoDisplay(DisplayMode, main_rgb)
                temp_led_strip_color_secondary = led_fx.getTipLEDStripValuestoDisplay(DisplayMode, tip_rgb)

                for i in range(len(main_rgb)):
                    main_rgb[i] = main_rgb[i] * temp_strip_led_brightness / 255.0

                ## A list is generated here that contains an rgb array for every led in the list.
                ## The idea here is that multiple pulses could overlap one another, so the program needs to keep a base print output so
                ## that the proper pulse color can be generated (even if they overlap)
                ## If there was a way to do it all at once, without the printlist, that would be much prefered
                print_list = []
                for i in range(0, led_strip_length):
                    print_list.append(main_rgb)


                for i in range(len(pulse_list)):
                    p = pulse_list[i]
                    
                    ## Draw the entire pulse, including the tail on the list to print
                    for tail_i in range(p.tail):
                        if 0 <= p.x_location - tail_i and p.x_location - tail_i < led_strip_length:
                            print_list[p.x_location - tail_i] = p.getDisplayColor(main_rgb, tip_rgb, tail_i)
                    p.moveRight()


                strip = drawList(strip, print_list)
    #            for i in range(len(print_list)):
    #                display_rgb = print_list[i]
    #                display_color = Color(int(display_rgb[0]), int(display_rgb[1]), int(display_rgb[2]))
    #                strip.setPixelColor(i, display_color)
                strip.show()

                pulse_list = removeAnyOldPulses(pulse_list)
                
            time.sleep(pause_time)
                
        
# Main function
if __name__ == "__main__":
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()
    spectrumPulse(strip, )
