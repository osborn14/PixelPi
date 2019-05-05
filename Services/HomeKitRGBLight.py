import logging, signal, threading

import Keys.Settings as SETTINGS

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_LIGHTBULB

from Data.HomeKitData import HomeKitData

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")


class HomeKitRGBLight(Accessory):

    category = CATEGORY_LIGHTBULB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_settings = None
        self.out_queue = None

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

    def setQueueAndSettings(self, out_queue, interface_settings):
        self.interface_settings = interface_settings
        self.out_queue = out_queue

    def set_state(self, value):
        self.accessory_state = value
        if value == 1:  # On
            self.set_hue(self.hue)
        else:
            self.update_light_with_color(0, 0, 0)  # Off

    def set_hue(self, value):
        # Lets only write the new RGB values if the power is on
        # otherwise update the hue value only
        if self.accessory_state == 1:
            self.hue = value
            rgb_tuple = self.hsv_to_rgb(
                self.hue, self.saturation, self.brightness)
            if len(rgb_tuple) == 3:
                self.update_light_with_color(
                    rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        else:
            self.hue = value

    def set_brightness(self, value):
        self.brightness = value
        self.set_hue(self.hue)

    def set_saturation(self, value):
        self.saturation = value
        self.set_hue(self.hue)

    def update_light_with_color(self, red, green, blue):
        color_dict = {
            SETTINGS.RED: red,
            SETTINGS.GREEN: green,
            SETTINGS.BLUE: blue
        }

        print(color_dict)

        home_kit_data = HomeKitData(service=SETTINGS.HOMEKIT)
        home_kit_data.setDataFromDict(color_dict)

        self.out_queue.put(home_kit_data)

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


class HomeKitWhiteLight(Accessory):

    category = CATEGORY_LIGHTBULB

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set our neopixel API services up using Lightbulb base
        serv_light = self.add_preload_service(
            'Lightbulb', chars=['On', 'Brightness'])

        # Configure our callbacks
        self.char_on = serv_light.configure_char(
            'On', setter_callback=self.set_state)
        self.char_on = serv_light.configure_char(
            'Brightness', setter_callback=self.set_brightness)

        # Set our instance variables
        self.accessory_state = 0  # State of the neo light On/Off
        self.brightness = 100  # Brightness value 0 - 100 Homekit API

    def setQueueAndSettings(self, out_queue, interface_settings):
        self.interface_settings = interface_settings
        self.out_queue = out_queue

    def set_state(self, value):
        self.accessory_state = value
        if value == 1:  # On
            self.set_brightness(100)
        else:
            self.set_brightness(0)  # Off

    def set_brightness(self, value):
        self.brightness = value
        self.update_light_with_color(self.value)

    def update_light_with_color(self, brightness):
        color_dict = {
            SETTINGS.WHITE: int(brightness * 255 / 100)
        }

        home_kit_data = HomeKitData(service=SETTINGS.HOMEKIT)
        home_kit_data.setDataFromDict(color_dict)

        self.out_queue.put(home_kit_data)


class HomeKitDeviceRunner:
    def __init__(self, interface_settings, out_queue):
        self.interface_settings = interface_settings
        self.out_queue = out_queue

        self.driver = AccessoryDriver(port=51826)
        self.driver.add_accessory(accessory=self.get_accessory(self.driver))
        signal.signal(signal.SIGTERM, self.driver.signal_handler)

    def run(self):
        driver_thread = threading.Thread(target=self.driver.start)
        driver_thread.setDaemon(True)
        driver_thread.start()

    def get_bridge(self, driver):
        """Call this method to get a Bridge instead of a standalone accessory."""
        bridge = Bridge(driver, 'Bridge')

        rgb_light = HomeKitRGBLight(driver, self.interface_settings[SETTINGS.UNIQUE_IDENTIFIER])
        rgb_light.setQueueAndSettings(self.out_queue, self.interface_settings)
        bridge.add_accessory(rgb_light)

        return bridge

    def get_accessory(self, driver):
        """Call this method to get a standalone Accessory."""

        white_lights = [SETTINGS.FIFTY_FIFTY_WHITE]
        rgb_lights = [SETTINGS.NEOPIXEL, SETTINGS.FIFTY_FIFTY, SETTINGS.FIFTY_FIFTY_RGB]

        if self.interface_settings[SETTINGS.INTERFACE] in white_lights:
            light = HomeKitWhiteLight(driver, self.interface_settings[SETTINGS.UNIQUE_IDENTIFIER])

        elif self.interface_settings[SETTINGS.INTERFACE] in rgb_lights:
            light = HomeKitRGBLight(driver, self.interface_settings[SETTINGS.UNIQUE_IDENTIFIER])

            light.setQueueAndSettings(self.out_queue, self.interface_settings)

        return light


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')
    # temp_sensor = TemperatureSensor(driver, 'Sensor 2')
    # temp_sensor2 = TemperatureSensor(driver, 'Sensor 1')
    # bridge.add_accessory(temp_sensor)
    # bridge.add_accessory(temp_sensor2)

    neopixel_one = HomeKitRGBLight(driver, 'Pixel 1')
    bridge.add_accessory(neopixel_one)

    return bridge


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return HomeKitRGBLight(driver, 'NeopixelTest')


# if __name__ == "__main__":
    # policy = asyncio.get_event_loop_policy()
    # policy.set_event_loop(policy.new_event_loop())
    # runner = HomeKitDeviceRunner({}, Queue(), asyncio.get_event_loop())
    # runner.start()

    # Start the accessory on port 51826
    # driver = AccessoryDriver(port=51826)

    # Change `get_accessory` to `get_bridge` if you want to run a Bridge.
    # driver.add_accessory(accessory=get_accessory(driver))

    # We want SIGTERM (terminate) to be handled by the driver itself,
    # so that it can gracefully stop the accessory, server and advertising.
    # signal.signal(signal.SIGTERM, driver.signal_handler)

    # Start it!
    # driver_thread = threading.Thread(target=driver.start())
    # driver_thread.start()
    # driver.start()

