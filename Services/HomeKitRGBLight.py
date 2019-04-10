import logging
import signal

import Keys.Settings as SETTINGS

from multiprocessing import Process
from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_LIGHTBULB

from Data.HomeKitData import HomeKitData

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class HomeKitRGBLight(Accessory):

    category = CATEGORY_LIGHTBULB

    def __init__(self, out_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.out_queue = out_queue

        # Set our neopixel API services up using Lightbulb base
        serv_light = self.add_preload_service(
            'Lightbulb', chars=['On', 'Hue', 'Saturation', 'Brightness'])

        # Configure our callbacks
        self.char_hue = serv_light.configure_char(
            'Hue', setter_callback=self.set_hue)
        self.char_saturation = serv_light.configure_char(
            'Saturation', setter_callback=self.set_saturation)
        self.char_on = serv_light.configure_char(
            'On', setter_callback=self.set_state)
        self.char_on = serv_light.configure_char(
            'Brightness', setter_callback=self.set_brightness)

        # Set our instance variables
        self.accessory_state = 0  # State of the neo light On/Off
        self.hue = 0  # Hue Value 0 - 360 Homekit API
        self.saturation = 100  # Saturation Values 0 - 100 Homekit API
        self.brightness = 100  # Brightness value 0 - 100 Homekit API

        # self.is_GRB = is_GRB  # Most neopixels are Green Red Blue
        # self.LED_count = LED_count

        # ------------------ TESTING VARIABLES ---------------------
        self.is_GRB = True  # Most neopixels are Green Red Blue
        self.LED_count = 50
        # --------------------- END TESTING ------------------------

    def set_state(self, value):
        self.accessory_state = value
        if value == 1:  # On
            self.set_hue(self.hue)
        else:
            self.update_neopixel_with_color(0, 0, 0)  # Off

    def set_hue(self, value):
        # Lets only write the new RGB values if the power is on
        # otherwise update the hue value only
        if self.accessory_state == 1:
            self.hue = value
            rgb_tuple = self.hsv_to_rgb(
                self.hue, self.saturation, self.brightness)
            if len(rgb_tuple) == 3:
                self.update_neopixel_with_color(
                    rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        else:
            self.hue = value

    def set_brightness(self, value):
        self.brightness = value
        self.set_hue(self.hue)

    def set_saturation(self, value):
        self.saturation = value
        self.set_hue(self.hue)

    def update_neopixel_with_color(self, red, green, blue):
        color_dict = {
            SETTINGS.RED: red,
            SETTINGS.GREEN: green,
            SETTINGS.BLUE: blue
        }

        home_kit_data = HomeKitData(service=SETTINGS.HOMEKIT)
        home_kit_data.setDataFromDict(color_dict)

        self.out_queue.add(home_kit_data)

    def hsv_to_rgb(self, h, s, v):

        hPri = h / 60
        s = s / 100
        v = v / 100

        if s <= 0.0:
            return int(0), int(0), int(0)

        C = v * s  # Chroma
        X = C * (1 - abs(hPri % 2 - 1))

        RGB_Pri = [0.0, 0.0, 0.0]

        if 0 <= hPri <= 1:
            RGB_Pri = [C, X, 0]
        elif 1 <= hPri <= 2:
            RGB_Pri = [X, C, 0]
        elif 2 <= hPri <= 3:
            RGB_Pri = [0, C, X]
        elif 3 <= hPri <= 4:
            RGB_Pri = [0, X, C]
        elif 4 <= hPri <= 5:
            RGB_Pri = [X, 0, C]
        elif 5 <= hPri <= 6:
            RGB_Pri = [C, 0, X]
        else:
            RGB_Pri = [0, 0, 0]

        m = v - C

        return int((RGB_Pri[0] + m) * 255), int((RGB_Pri[1] + m) * 255), int((RGB_Pri[2] + m) * 255)


class HomeKitDeviceRunner(Process):
    def __init__(self, out_queue):
        super(HomeKitDeviceRunner, self).__init__()
        self.out_queue = out_queue

        self.driver = AccessoryDriver(port=51826)
        self.driver.add_accessory(accessory=self.get_accessory(self.driver))
        self.signal.signal(signal.SIGTERM, self.driver.signal_handler)

    def run(self):
        self.driver.start()

    def get_bridge(self, driver):
        """Call this method to get a Bridge instead of a standalone accessory."""
        bridge = Bridge(driver, 'Bridge')

        neopixel_one = HomeKitRGBLight(driver, 'Pixel 1', out_queue=out_queue)
        bridge.add_accessory(neopixel_one)

        return bridge

    def get_accessory(self, driver):
        """Call this method to get a standalone Accessory."""
        return HomeKitRGBLight(driver, 'Neopixel')
