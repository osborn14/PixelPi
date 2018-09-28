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
    

def getDisplayModeTwoColors(column_number, total_bars=16):
    columns_per_category = total_bars / 8
    column_category = column_number / columns_per_category
    # if column_category < 1:
    #     rgb = [255, 0, 0]
    #
    # elif column_category < 2:
    #     rgb = [255, 165, 0]
    #
    # elif column_category < 3:
    #     rgb = [255, 215, 0]
    #
    # elif column_category < 4:
    #     rgb = [34, 139, 34]
    #
    # elif column_category < 5:
    #     rgb = [0, 255, 0]
    #
    # elif column_category < 6:
    #     rgb = [0, 0, 255]
    #
    # elif column_category < 7:
    #     rgb = [25, 25, 112]
    #
    # elif column_category <= 8:
    #     rgb = [75, 0, 130]

    rgb_dict = {
        0: [255, 0, 0],
        1: [255, 165, 0],
        2: [255, 215, 0],
        3: [34, 139, 34],
        4: [0, 255, 0],
        5: [0, 0, 255],
        6: [25, 25, 112],
        7: [75, 0, 130]
    }

    rgb = rgb_dict[column_category]

    return rgb

def getDisplayModeThreeColors(main_rgb, tip_rgb, bar_i, total_bars):
    rgb = [0, 0, 0]
    bass_rgb = main_rgb
    treble_rgb = tip_rgb

    for i in range(len(rgb)):
        rgb[i] = (bass_rgb[i] * (1 - (bar_i/total_bars))) + (treble_rgb[i] * (bar_i/total_bars))
    
    return rgb

def getFadedColors(FADE_START, FADE_END, upper_transition_range, current_value, drawline, rgb, lower_rgb):
    transition_range = FADE_END - FADE_START + 1
    temp_rgb = [0, 0, 0]
    increment_rgb = [0, 0, 0]

    ## If the pixel if above the threshold to start a transition
    if current_value+1 > FADE_START:
        for i in range(len(increment_rgb)):
            increment_rgb[i] = (rgb[i] - lower_rgb[i]) / transition_range * 1.0

    ## If the pixel is within the transistion range
    if drawline <= current_value - FADE_START and drawline >= current_value - FADE_END:
        incrementfactor = current_value - upper_transition_range - (upper_transition_range - drawline) + 2
        
        for i in range(len(increment_rgb)):
            temp_rgb[i] = lower_rgb[i] + increment_rgb[i] * incrementfactor * 1.0
            
    ## If the pixel is below the transition point
    elif drawline < current_value - FADE_END:
        temp_rgb = lower_rgb

    ## If the pixel does not need any sort of transition, set it to the normal color
    else:
        temp_rgb = rgb

    dimmer = (32 - drawline) / 32  * 1.0
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


def getAverageofListValues(datalist, lower_item, upper_item):
    avg = 0
    
    for fa in range(lower_item, upper_item):
        avg = datalist[fa] + avg
    avg = avg / (upper_item - lower_item)

    return avg

def calculateBarHeight(main_height, tip_height, bar_i):
    if main_height[bar_i] == 0 and tip_height[bar_i] == 1:
        tip_height[bar_i] = 0
    elif main_height[bar_i] < tip_height[bar_i]-1:
        tip_height[bar_i] = tip_height[bar_i] - 1
    else:
        tip_height[bar_i] = main_height[bar_i] + 1

    return tip_height[bar_i]

def applyGradientEffects(main_rgb, tip_rgb, DisplayMode, bar_i):
    rgb = main_rgb
    if DisplayMode == 1:
        rgb = getDisplayModeTwoColors(bar_i)
    elif DisplayMode == 2:
        rgb = getDisplayModeThreeColors(main_rgb, tip_rgb, bar_i, 16)

    return rgb

def getTipColor(DisplayMode, main_rgb, tip_rgb):
    if DisplayMode == 1 or DisplayMode == 2:
        tip_rgb = main_rgb
    
    return tip_rgb


def getDataListtoPrint(prev_main_height, new_spectrum_heights):
    for i in range(len(prev_main_height)):
        prev_main_height[i] = prev_main_height[i] - 3 if prev_main_height[i] - 3 > new_spectrum_heights[i] else new_spectrum_heights[i]
        prev_main_height[i] = 1 if prev_main_height[i] < 1 else prev_main_height[i]
        # if prev_main_height[i] - 3 > new_spectrum_heights[i]:
        #     prev_main_height[i] = prev_main_height[i] - 3
        # else:
        #     prev_main_height[i] = new_spectrum_heights[i]

        #if main_height[i] < 0:
         #   main_height[i] = 0

    return prev_main_height
