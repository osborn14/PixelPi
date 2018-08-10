#!/usr/bin/env python

def calculateIndividualTransition(main, nextmain):
    if main - nextmain < 5 and main - nextmain > -5:
        main = nextmain
    elif main - nextmain >= 5:
        main = main - 5
    elif main - nextmain <= -5:
        main = main + 5
    return main

def calculateTransition(rgb, next_rgb):
    if next_rgb[0] != rgb[0] or next_rgb[1] != rgb[1] or next_rgb[2] != rgb[2]:
        for i in range(len(rgb)):
            rgb[i] = calculateIndividualTransition(rgb[i], next_rgb[i])
    return rgb

def getDisplayModeTwoColors(column_number):
    if column_number == 1 or column_number == 2:
        rgb = [255, 0, 0]
                    
    elif column_number == 3 or column_number == 4:
        rgb = [255, 165, 0]
                    
    elif column_number == 5 or column_number == 6:
        rgb = [255, 215, 0]
            
    elif column_number == 7 or column_number == 8:
        rgb = [34, 139, 34]

    elif column_number == 9 or column_number == 10:
        rgb = [0, 255, 0]

    elif column_number == 11 or column_number == 12:
        rgb = [0, 0, 255]

    elif column_number == 13 or column_number == 14:
        rgb = [25, 25, 112]

    else:
        rgb = [75, 0, 130]

    return rgb

def getDisplayModeThreeColors(main_rgb, tip_rgb, bar_i, total_bars):
    rgb = [0, 0, 0]
    bass_rgb = main_rgb
    treble_rgb = tip_rgb

    for i in range(len(rgb)):
        rgb[i] = (bass_rgb[i] * (1 - (bar_i/total_bars))) + (treble_rgb[i] * (bar_i/total_bars))
    
    return rgb

def getFadedColors(fade_start, fade_end, uppertransitionrange, main_height, bar_i, drawline, rgb, lower_rgb):
    fade_start = 8
    fade_end = 17

    transition_range = fade_end - fade_start + 1
    temp_rgb = [0, 0, 0]
    increment_rgb = [0, 0, 0]

    ## If the pixel if above the threashold to start a transition
    if main_height[bar_i]+1 > fade_start:
        for i in range(len(increment_rgb)):
            increment_rgb[i] = (rgb[i] - lower_rgb[i]) / transition_range

    ## If the pixel is within the transistion range
    if drawline <= main_height[bar_i] - fade_start and drawline >= main_height[bar_i] - fade_end:
        incrementfactor = main_height[bar_i] - uppertransitionrange - (uppertransitionrange - drawline) + 2

        for i in range(len(increment_rgb)):
            temp_rgb[i] = lower_rgb[i] + increment_rgb[i] * incrementfactor
            
    ## If the pixel is below the transition point
    elif drawline < main_height[bar_i] - fade_end:
        temp_rgb = lower_rgb

    ## If the pixel does not need any sort of transition, set it to the normal color
    else:
        temp_rgb = rgb

    dimmer = (32 - drawline) / 32
    return_rgb = [0, 0, 0]
    
    for i in range(len(temp_rgb)):
        return_rgb[i] = int(dimmer * float(temp_rgb[i]))
    
    return return_rgb

def calculateStripLEDBrightness(strip_led_brightness, avg):
    if 255 * (avg/32) > strip_led_brightness:
        strip_led_brightness = int(255 * (avg/32))
    else:
        if strip_led_brightness > 75:
            strip_led_brightness = strip_led_brightness - 2.5
        elif strip_led_brightness > 0:
            strip_led_brightness = strip_led_brightness - 1.0

        if strip_led_brightness < 0:
            strip_led_brightness = 0

    return strip_led_brightness

def calculateTempStripLEDBrightness(strip_led_brightness, strip_led_brightness_multiplier, minimum_brightness = 0):
    temp_strip_led_brightness = int(strip_led_brightness_multiplier * strip_led_brightness)
    
    if temp_strip_led_brightness > 255:
        temp_strip_led_brightness = 255
    elif temp_strip_led_brightness < minimum_brightness:
        temp_strip_led_brightness = minimum_brightness
    
    return temp_strip_led_brightness

def returnUsableServerData(rawdata, expected_array_list_size):
    data = rawdata.decode('utf-8')
    if "n" in data:
        data = data.replace("n", "")
    datalist = data.split(" ")
    ltcounter = False
    datalist = list(map(int, datalist))
    datalistlen = len(datalist)
    
    while datalistlen > expected_array_list_size:
        del datalist[datalistlen-2]
        datalistlen -= 1
        
    return datalist

def getDataListtoPrint(main_height, datalist, lower_item, upper_item):
    for fa in range(lower_item, upper_item):
        if main_height[fa] - 3 > datalist[fa]:
            main_height[fa] = main_height[fa] - 3
        else:
            main_height[fa] = datalist[fa]

        if main_height[fa] < 1:
            main_height[fa] = 1

    return main_height

def getAverageofListValues(datalist, lower_item, upper_item):
    avg = 0
    
    for fa in range(lower_item, upper_item):
        avg = datalist[fa] + avg
    avg = avg / (upper_item - lower_item)

    return avg

def calculateBarHeight(main_height, tip_height, bar_i):
    if main_height[bar_i] == 0 and tip_height[bar_i+1] == 1:
        tip_height[bar_i+1] = 0
    elif main_height[bar_i] < tip_height[bar_i+1]-1:
        tip_height[bar_i+1] = tip_height[bar_i+1] - 1
    else:
        tip_height[bar_i+1] = main_height[bar_i] + 1

    return tip_height[bar_i+1]

def applyGradientEffects(main_rgb, tip_rgb, DisplayMode, bar_i):
    rgb = main_rgb
    if DisplayMode == 2:
        rgb = getDisplayModeTwoColors(bar_i)
    elif DisplayMode == 3:
        rgb = getDisplayModeThreeColors(main_rgb, tip_rgb, bar_i, 16)

    return rgb

def getTipColor(DisplayMode, main_rgb, tip_rgb):
    if DisplayMode == 2 or DisplayMode == 3:
        tip_rgb = main_rgb
    
    return tip_rgb

def getMainLEDStripValuestoDisplay(DisplayMode, main_rgb):
    temp_led_strip_color_main = [0, 0, 0]
    if DisplayMode == 0 or DisplayMode == 3:
        temp_led_strip_color_main = main_rgb
    
    if DisplayMode == 2:
        temp_led_strip_color_main = main_rgb
    
    return temp_led_strip_color_main

def getTipLEDStripValuestoDisplay(DisplayMode, tip_rgb):
    temp_led_strip_color_secondary = [0, 0, 0]
    if DisplayMode == 0 or DisplayMode == 3:
        temp_led_strip_color_secondary = tip_rgb
    
    if DisplayMode == 2:
        temp_led_strip_color_secondary = [255, 255, 255]
    
    return temp_led_strip_color_secondary
