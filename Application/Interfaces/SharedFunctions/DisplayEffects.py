class Mode():
    def __init__(self, rgb):
        self.rgb_values = rgb


class Timer(Mode):
    def __init__(self, day, hour, minute, rgb_array):
        super().__init__(self.rgb)
        self.day = day
        self.hour = hour
        self.minute = minute
        self.rgb_array = rgb_array
        self.activated = False


class Sparkle(Mode):
    ## Class that stores values for sparkle mode
    def __init__(self, rgb):
        super().__init__(rgb)
        self.sparkle_rgb_list = list()
        print("sparkler init called")

        i = 0
        increasing = True
        for rgb_array in self.rgb_values:
            print("rgb array --- ", rgb_array)
            multiplier_values = [int(rgb_array[0] / 10), int(rgb_array[1] / 10), int(rgb_array[2] / 10)]

            if i > 0:
                i = 0
                increasing = True
                current_rgb_values = [int(rgb_array[0] / 10), int(rgb_array[1] / 10), int(rgb_array[2] / 10)]
                self.sparkle_rgb_list.append(SparkleRGB(rgb_array, current_rgb_values, multiplier_values, increasing))

            else:
                i += 1
                increasing = False

                current_rgb_values = rgb_array
                self.sparkle_rgb_list.append(SparkleRGB([0, 0, 250], current_rgb_values, multiplier_values, increasing))

    def getCurrentRgbValues(self):
        rgb_list = list()
        print(self.rgb_values)
        for s in self.sparkle_rgb_list:
            rgb_list.append(s.getCurrentRgbValue())

        return rgb_list


class SparkleRGB():
    ## Stores values of a single color in a Sparkle dispaly mode
    def __init__(self, init_rgb, current_rgb, multiplier, increasing):
        self.init_rgb = init_rgb
        self.current_rgb = current_rgb
        self.multiplier = multiplier
        self.increasing = increasing

    def getCurrentRgbValue(self):
        if self.increasing:
            for i in range(len(self.current_rgb)):
                self.current_rgb[i] = self.current_rgb[i] + self.multiplier[i]
            if self.current_rgb[0] >= self.init_rgb[0] and self.current_rgb[1] >= self.init_rgb[1] and self.current_rgb[
                2] >= self.init_rgb[2]:
                self.increasing = False

        else:
            for i in range(len(self.current_rgb)):
                self.current_rgb[i] = self.current_rgb[i] - self.multiplier[i]
            if self.current_rgb[0] <= 0 and self.current_rgb[1] <= 0 and self.current_rgb[2] <= 0:
                self.current_rgb[0] = 0
                self.current_rgb[1] = 0
                self.current_rgb[2] = 0
                self.increasing = True

        print("init value: " + str(self.init_rgb))
        print("current value: " + str(self.current_rgb))

        return self.current_rgb
