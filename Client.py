import sys, time, asyncio, threading

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS
import Settings.Config as Config

from Audio.AudioData import AudioData

from Networking.Client import MyClientProtocol
from autobahn.asyncio.websocket import WebSocketClientFactory


def gatherClient(self):
    try:
        client_settings = Config.client

    except NameError:
        print("No client detected...")
        return None

    interface_dict_list = Config.client[SETTINGS.INTERFACE_LIST]
    interface_obj_list = self.getInterfaces(interface_dict_list)

    return Client(client_settings, interface_obj_list)


class Client:
    def __init__(self, settings):
        self.settings = settings
        interface_list = self.getInterfaces(settings)

        self.twisted_factory = WebSocketClientFactory(u"ws://" + settings[SETTINGS.SERVER_IP_ADDRESS] + ":" + str(9000))
        self.twisted_factory.protocol = MyClientProtocol
        self.twisted_factory.protocol.setClassVariables(settings, interface_list)

    def run(self):
        connection_to_audio_server_thread = threading.Thread(target=self.displayLights)
        connection_to_audio_server_thread.setDaemon(True)
        connection_to_audio_server_thread.start()

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(self.twisted_factory, self.settings[SETTINGS.SERVER_IP_ADDRESS], 9000)

        while True:
            loop.run_until_complete(coro)

            try:
                loop.run_forever()
            except:
                print("Connection to server lost!")
            finally:
                loop.close()

            time.sleep(1)

    def displayLights(self):
        while True:
            print("In while loop")
            if not NETWORK.remove_queue.empty():
                print("Retrieved from remove queue!")
                self.processServerJson(NETWORK.remove_queue.get())

            elif not NETWORK.display_queue.empty():
                print("Retrieved from display queue!")
                self.processServerJson(NETWORK.display_queue.get())

            elif not NETWORK.audio_queue.empty():
                print("Audio [playing")
                last_played_time = time.time()
                audio_data = AudioData()

                while True:
                    if not NETWORK.audio_queue.empty():
                        last_played_time = time.time()

                        audio_dict = NETWORK.audio_queue.get()
                        audio_data.setAudioDataFromJSON(audio_dict[NETWORK.AUDIO_DATA])

                    elif time.time() - last_played_time >= 45:
                        break;

                    else:
                        audio_data.setSpectrumToZero()

                    for interface in self.interface_list:
                        interface.displayAudioLights(audio_data)

            else:
                for interface in self.interface_list:
                    interface.displayNormalLights()

                time.sleep(.1)

    def processServerJson(self, msg):
        print("Processing server json!")
        for interface in self.interface_list:
            if interface.unique_identifier == msg[SETTINGS.UNIQUE_IDENTIFIER]:
                if msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
                    if msg[NETWORK.DISPLAY_EFFECT] == NETWORK.SIMPLE:
                        interface.task_list.append(Simple(msg))

                if msg[NETWORK.COMMAND] == NETWORK.REMOVE:
                    for remove_id in msg[NETWORK.REMOVE_LIST]:
                        interface.task_list = list(
                            filter(lambda task: task.task_id != remove_id, interface.task_list))

        print(msg)

    def getInterfaces(self, settings):
        # TODO: Do check for required settings!
        interface_list = list()

        for interface in settings[SETTINGS.INTERFACE_LIST]:
            if interface[SETTINGS.INTERFACE] == SETTINGS.MATRIX:
                from Interfaces.Matrix import Matrix

                matrix_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_MATRIX,
                    SETTINGS.MILITARY_TIME: False
                }

                matrix_settings = self.getSettingsWithDefault(settings[SETTINGS.MATRIX],
                                                              matrix_default_settings)
                interface_list.append(Matrix(matrix_settings))

            if interface[SETTINGS.INTERFACE] == SETTINGS.NEOPIXEL:
                from Interfaces.Neopixel import Neopixel

                # TODO: Create audio dimmer setting
                neopixel_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_NEOPIXEL,
                    SETTINGS.AUDIO_DIMMER: 1
                }

                neopixel_settings_list = list(
                    map(lambda settings: self.getSettingsWithDefault(settings, neopixel_default_settings),
                        settings[SETTINGS.NEOPIXEL]))

                neopixel_list = list(map(lambda settings: Neopixel(settings), neopixel_settings_list))
                interface_list.extend(neopixel_list)

            if interface[SETTINGS.INTERFACE] == SETTINGS.FIFTY_FIFTY:
                from Interfaces.FiftyFifty import FiftyFifty

                fifty_fifty_default_settings = {
                    SETTINGS.CODE: SETTINGS.CODE_FIFTY_FIFTY,
                    SETTINGS.BRIGHTNESS_MULTIPLIER: 1.4,
                    SETTINGS.AUDIO_DIMMER: 1
                }

                fifty_fifty_settings_list = list(
                    map(lambda settings: self.getSettingsWithDefault(settings, fifty_fifty_default_settings),
                        settings[SETTINGS.FIFTY_FIFTY]))

                fifty_fifty_list = list(map(lambda settings: FiftyFifty(settings), fifty_fifty_settings_list))
                interface_list.extend(fifty_fifty_list)

        if len(interface_list) == 0:
            print("No interfaces detected!")
            sys.exit()

        return interface_list

    def getSettingsWithDefault(self, settings, defaults):
        for key, value in defaults.items():
            if key not in settings:
                settings[key] = value

        return settings


if __name__ == "__main__":
    client = Config.client
    client.run()