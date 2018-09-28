import math


class MatrixDisplayMode():
    def __init__(self, audio_data):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.upper_transition_range = 0
        self.fade_start = 8
        self.fade_end = 17
        self.audio_data = audio_data
        self.spectrum_list_len = len(self.audio_data.spectrum_heights)

    # def setX(self, x):
    #     if x >= self.fade_start:
    #         self.upper_transition_range = x - self.fade_start

    def getFadedColors(self, max_y, current_y, rgb):
        transition_range = self.fade_end - self.fade_start + 1
        temp_rgb = increment_rgb = [0, 0, 0]

        ## If the pixel if above the threshold to start a transition
        if max_y + 1 > self.fade_start:
            for i in range(len(increment_rgb)):
                increment_rgb[i] = (rgb[i] - self.lower_main_rgb[i]) / transition_range * 1.0

        ## If the pixel is within the transistion range
        if current_y <= max_y - self.fade_start and current_y >= max_y - self.fade_end:
            incrementfactor = max_y - self.upper_transition_range - (self.upper_transition_range - current_y) + 2

            for i in range(len(increment_rgb)):
                temp_rgb[i] = self.lower_main_rgb[i] + increment_rgb[i] * incrementfactor * 1.0

        ## If the pixel is below the transition point
        elif current_y < max_y - self.fade_end:
            temp_rgb = self.lower_main_rgb

        ## If the pixel does not need any sort of transition, set it to the normal color
        else:
            temp_rgb = rgb

        dimmer = (32 - current_y) / 32 * 1.0
        return_rgb = [0, 0, 0]

        for i in range(len(temp_rgb)):
            return_rgb[i] = int(dimmer * float(temp_rgb[i]))

        return return_rgb

    # def calculateMainHeightsList(self):
    #     raise NotImplementedError
    #
    # def calculateTipHeightList(self):
    #     raise NotImplementedError

    def displayFrame(self):
        raise NotImplementedError

class Flat(MatrixDisplayMode):
    def __init__(self, matrix, audio_data):
        super().__init__(matrix, audio_data)
        self.lower_main_rgb = [255, 255, 255]
        self.bar_width = self.matrix_width / self.spectrum_list_len

    # def calculateMainHeightList(self, main_height_list, matrix_width):
    #     height_list = list()
    #     bar_width = matrix_width / len(main_height_list)
    #
    #     for x in range(matrix_width):
    #         y_height = None if (x + 1) % bar_width == 0 else main_height_list[int(x/bar_width)]
    #         height_list.append(y_height)
    #
    #     return height_list

    # def calculateTipHeightList(self, y_height_list, adjusted_tip_height_list):
    #     tip_height_list = list()
    #
    #
    #     for x in range(self.matrix_width):
    #         y_height = 0 if (x + 1) % bar_width == 0 else main_height_list[int(x / bar_width)]
    #         height_list.append(y_height)
    #
    #     return height_list
    #
    # def calculateHeightList(self, ):
    #     height_list = list()
    #     bar_width = matrix_width / len(main_height_list)
    #
    #     for x in range(matrix_width):
    #         y_height = 0 if (x + 1) % bar_width == 0 else main_height_list[int(x / bar_width)]
    #         height_list.append(y_height)
    #
    #     return height_list

    # def getTipColor(server_primary_colors, server_secondary_colors):
    #     return server_secondary_colors

    def getFrame(self, main_height_list, tip_height_list):
        for bar in range(self.spectrum_list_len):
            for i in range(self.spectrum_list_len - 1):
                x = bar * self.bar_width + i
                max_y = main_height_list[bar]
                for y in range(max_y):
                    main_display_rgb = self.getFadedColors(max_y, y, self.audio_data.server_primary_colors)
                    self.offscreen_canvas.SetPixel(x, 32 - y, main_display_rgb[0], main_display_rgb[1], main_display_rgb[2])

                tip_rgb = self.audio_data.server_secondary_colors
                self.offscreen_canvas.SetPixel(x, 32 - tip_height_list[bar], tip_rgb[0], tip_rgb[1], tip_rgb[2])

        return self.offscreen_canvas


#class Rainbow(MatrixDisplayMode):

#class Gradient(MatrixDisplayMode):

class Singles(MatrixDisplayMode):
    def __init__(self, main_height_list, tip_height, LED_MATRIX_WIDTH, individual_spectrum_length):
        self.spectrums_per_matrix = int(LED_MATRIX_WIDTH / individual_spectrum_length)
        self.spectrums_per_category = self.spectrums_per_matrix / 4

        self.main_height_list = main_height_list
        self.tip_height_list = tip_height

        self.shortened_main_height_list = list(map(lambda single_height: math.ceil(single_height / 3), self.main_height_list))
        self.shortened_tip_height_list = list(map(lambda single_height: math.ceil(single_height / 3), self.tip_height_list))

        # self.reversed_main_height = list(reversed(main_height))
        # self.reversed_tip_height = list(reversed(tip_height))
        # self.shortened_main_height = []
        # self.shortened_tip_height = []
        # for i in range(len(main_height)):
        #     self.shortened_main_height.append(math.ceil(main_height[len(main_height) - i - 1] / 3))
        #     self.shortened_tip_height.append(math.ceil(tip_height[len(tip_height) - i - 1] / 3))
        # self.reversed_shortened_main_height = list(reversed(self.shortened_main_height))
        # self.reversed_shortened_tip_height = list(reversed(self.shortened_tip_height))

    def getMainHeight(self, single_column_in_bar_i):
        chart_number = math.ceil((single_column_in_bar_i + 1) / self.spectrums_per_category)

        # if chart_number <= 1:
        #     temp_main_height = self.reversed_shortened_main_height
        # elif chart_number <= 2:
        #     temp_main_height = self.reversed_main_height
        # elif chart_number <= 3:
        #     temp_main_height = self.main_height
        # elif chart_number <= 4:
        #     temp_main_height = self.shortened_main_height

        main_height_dict = {
            1: list(reversed(self.shortened_main_height_list)),
            2: list(reversed(self.main_height_list)),
            3: self.main_height_list,
            4: self.shortened_main_height_lost
        }

        temp_main_height = main_height_dict[chart_number]

        return temp_main_height

    def getTipHeight(self, single_column_in_bar_i):
        chart_number = math.ceil((single_column_in_bar_i + 1) / self.spectrums_per_category)

        main_height_dict = {
            1: list(reversed(self.shortened_main_height_list)),
            2: list(reversed(self.main_height_list)),
            3: self.main_height_list,
            4: self.shortened_main_height_lost
        }

        if chart_number <= 1:
            temp_tip_height = self.reversed_shortened_tip_height
        elif chart_number <= 2:
            temp_tip_height = self.reversed_tip_height
        elif chart_number <= 3:
            temp_tip_height = self.tip_height
        elif chart_number <= 4:
            temp_tip_height = self.shortened_tip_height

        return temp_tip_height