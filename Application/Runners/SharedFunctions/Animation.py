import random

class RGBpixel(object):
    def __init__(self, x, y, rgb_array, dimmer = 1):
        self.x = x
        self.y = y
        self.rgb = [0, 0, 0]

        for i in range(len(self.rgb)):
            self.rgb[i] = rgb_array[i] * dimmer


class Animation(object):
    def __init__(self, x, y):
        self.starting_x = x
        self.starting_y = y
        self.lightning_counter = 0

    def drawWeather(self, weather, sunset_dimmer, isDay):
        pixel_array = []
        rain_height = 6
        
        if weather == "Clear":
            if isDay:
                pixel_array = self.drawSun(sunset_dimmer)
            else:
                pixel_array= self.drawMoon()
        
        if weather == "Clouds" or weather == "Rain" or weather == "Thunderstorm":
            pixel_array.extend(self.drawClouds(isDay, sunset_dimmer))
        if weather == "Rain" or weather == "Thunderstorm":
            pixel_array.extend(self.drawRain(isDay, sunset_dimmer, rain_height))
        if weather == "Thunderstorm":
            if self.lightning_counter == 2:
                pixel_array.extend(drawLightning(isDay))
            if self.lightning_counter >= 2:
                self.lightning_counter = 0
            else:
                self.lightning_counter = self.lightning_counter + 1

        return pixel_array


    def drawSun(self, dimmer):
        ## Draw a sun for the LED Matrix
        pixel_array = []
        rgb = [0, 0, 0]

        starting_x = self.starting_x
        starting_y = self.starting_y
        
        sun_size = 4
        inner_sun_size = 2
        space_between_rays = 2 + 1
        
        ## Draw a 4 x 4 box for the sun itself
        for ix in range(sun_size):
            for iy in range(sun_size):
                ## For the inner 2 x 2 box, change the color slightly
                if 0 < ix <= inner_sun_size and 0 < iy <= inner_sun_size:
                    rgb = [255 * dimmer, 255 * dimmer, 0]
                else:
                    rgb = [255 * dimmer, 160 * dimmer, 0]
                
                ## Create a RGB pixel and add it to our list
                p = RGBpixel(ix + starting_x + 3, iy + starting_y + 3, rgb)
                pixel_array.append(p)
        
        ## This code will add the "rays" to the sun
        for ix in range(0, 4):
            x = 3 * ix
            for iy in range(1,3):
                rgb = [255 * dimmer, random.randrange(125, 255) * dimmer, 0]
                
                ## Only draw the pixels that correspond to the corners of the sun
                y = 3 * iy
                if y == 12:
                    y = 0
                elif x == 3 and y == 3:
                    y = 0
                elif x == 6 and y == 3:
                    y = 0
                elif x == 3 and y == 6:
                    y = 9
                elif x == 6 and y == 6:
                    y = 9
                
                p = RGBpixel(x + starting_x, y + starting_y, rgb)
                pixel_array.append(p)
                
        return pixel_array

    def drawMoon(self):
        pixel_array = []
        moon_rgb = [5, 5, 5]

        starting_x = self.starting_x + 4
        starting_y = self.starting_y + 3
        
        ## To draw the moon, draw a black circle in a white circle and then add a star
        pixel_array.extend(self.drawCircle(moon_rgb, 5, starting_x, starting_y))
        pixel_array_clear = self.drawCircle([0, 0, 0], 4, starting_x + 2, starting_y - 2)
##        for pixel_to_remove in pixel_array_clear:
##            for pixel in pixel_array:
##                if pixel_to_remove.rgb == pixel.rgb:
##                    pixel_array.remove(pixel)
        pixel_array.extend(self.drawStar(2, starting_x, starting_y))
        
        return pixel_array

    def drawCircle(self, rgb, circle_radius, starting_x, starting_y):
        pixel_array = []
        for dcx in range(-circle_radius, circle_radius + 1):
            for dcy in range(-circle_radius, circle_radius + 1):
                if (dcx * dcx) + (dcy * dcy) < (circle_radius+.5) * (circle_radius+.5):
                    p = RGBpixel(dcx + starting_x, dcy + starting_y, rgb)
                    pixel_array.append(p)

        return pixel_array

    def drawStar(self, star_radius, starting_x, starting_y):
        pixel_array = []
        random_white_rgb = [0, 0, 0]
        for sx in range(-star_radius, star_radius + 1):
            for sy in range(-star_radius, star_radius + 1):
                if abs(sx) + abs(sy) < star_radius:
                    w = random.randrange(2, 5)
                    for i in range(len(random_white_rgb)):
                        random_white_rgb[i] = w
                    p = RGBpixel(sx + starting_x + 2 * star_radius, sy + starting_y - star_radius, random_white_rgb)
                    pixel_array.append(p)
                        
        w = random.randrange(2, 5)
        p = RGBpixel(starting_x + star_radius, starting_y - 2 * star_radius, [w, w, w])
        pixel_array.append(p)

        return pixel_array

    def drawClouds(self, isDay, sunset_dimmer):
        pixel_array = []
        rgb = [0, 0, 0]

        starting_x = self.starting_x
        starting_y = self.starting_y
        
        ## Draw a 5 x 10 box that will be the base of our cloud
        for ix in range(0, 11):
            for iy in range(0, 6):
                ## See if the pixel is in the middle of the could.  If it is, give it a random bright white
                if 1<ix<4 and 0<iy<5:
                    if isDay:
                        w = random.randrange(185, 255) * sunset_dimmer
                    else:
                        w = random.randrange(2, 5)
                    rgb = [w, w, w]
                elif 4<=ix<=6 and 3<iy<5:
                    if isDay:
                        w = random.randrange(185, 255) * sunset_dimmer
                    else:
                        w = random.randrange(2, 5)
                    rgb = [w, w, w]
                elif 6<ix<9 and 1<iy<5:
                    if isDay:
                        w = random.randrange(185, 255) * sunset_dimmer
                    else:
                        w = random.randrange(2, 5)
                    rgb = [w, w, w]
                else:
                    ## If the pixel is around the edge of our cloud, give it a dull gray color
                    if isDay:
                        gray = 128 * sunset_dimmer
                    else:
                        gray = 2
                    rgb = [gray, gray, gray]
                
                ## Chisel out the parts we don't need
                if ix == 0:
                    if iy == 0 or iy == 1 or iy ==2:
                        rgb = [0, 0, 0]
                elif ix == 1:
                    if iy == 0:
                        rgb = [0, 0, 0]
                elif ix == 4:
                    if iy == 0:
                        rgb = [0, 0, 0]
                elif ix == 5:
                    if iy == 0 or iy == 1:
                        rgb = [0, 0, 0]
                elif ix == 6:
                    if iy == 0:
                        rgb = [0, 0, 0]
                elif ix == 7:
                    if iy == 0:
                        rgb = [0, 0, 0]
                elif ix == 8:
                    if iy == 0:
                        rgb = [0, 0, 0]
                elif ix == 9:
                    if iy == 0 or iy == 1:
                        rgb = [0, 0, 0]
                elif ix == 10:
                    if iy == 0 or iy == 1 or iy == 2 or iy == 3:
                        rgb = [0, 0, 0]
                    
                p = RGBpixel(ix + self.starting_x, iy + self.starting_y, rgb)
                pixel_array.append(p)
                
        return pixel_array

    def drawRain(self, isDay, sunset_dimmer, rain_height):
        pixel_array = []
        rain_height = 6

        starting_x = self.starting_x
        starting_y = self.starting_y
        
        for ix in range(1, 10):
#            upper_y = ssy+6
#            lower_y = ssy+11
#            first_rain_x = 0 + random.randrange(0, 2)
#            second_rain_x = 3 + random.randrange(0, 2)
#            third_rain_x = 6 + random.randrange(0, 2)
#            first_rain_y = ssy+7
#            second_rain_y = ssy+7
#            third_rain_y = ssy+7
#            rain_x_array = [first_rain_x, second_rain_x, third_rain_x]
#            rain_y_array = [first_rain_y, second_rain_y, third_rain_y]

            for iy in range(0, 4):
                rgb = [0, 0, 0]
                if isDay:
                    rgb[2] = random.randrange(135, 255) * sunset_dimmer
                else:
                    rgb[2] = random.randrange(2, 5)
                
                if ix % 2 != 0:
                    p = RGBpixel(ix + starting_x, iy + starting_y + rain_height, rgb)
                    pixel_array.append(p)
        return pixel_array

    def drawLightning(self, isDay, rain_height, lightning_counter):
        pixel_array = []
        
        starting_x = self.starting_x
        starting_y = self.starting_y
        lightning_x_offset = 4
        
        if isDay:
            rgb = [255, 215, 0]
        else:
            rgb = [4, 3, 0]

        for iy in range(0, 4):
            tix = 0
            for ix in range(0, 2):
                if iy != 3 or ix != 1:
                    if iy > 1:
                        tix = -1
                    p = RGBpixel(ix + starting_x + lightning_x_offset + iy + tix, iy + starting_y + rain_height, rgb)
                    pixel_array.append(p)
                    
        return pixel_array

    
