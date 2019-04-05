

import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Keys.Network as NETWORK

from multiprocessing import Queue

import Keys.Settings as SETTINGS

# from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
# from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor

from multiprocessing import Process


import Settings.Config as Config

from Data.AudioData import AudioData
from Data.WeatherData import WeatherData

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

server_msg_queue = Queue()


def runInterfaces(data_queue, interface_list):
    # process_network_msg_dict = {
    #     NETWORK.DISPLAY: self.processDisplay,
    #     NETWORK.REMOVE: self.processRemove
    # }

    fps = 20

    data_objects_dict = {
        SETTINGS.SPECTRUM_ANALYZER: AudioData,
        # SETTINGS.WEATHER: WeatherData
    }

    for data_object in data_objects_dict.values():
        data_object().ensureImportantPropertiesAreSet()

    while True:

        frame_start_time = time.time()

        data_dict_list = list()
        data_list = list()

        # Quickly get all data dictionaries
        while not data_queue.empty():
            data_dict_list.append(data_queue.get())

        # print(len(data_dict_list))

        # For each data object in the data_queue, create a data object
        for dict_from_server in data_dict_list:
            # print(type(dict_from_server))
            if SETTINGS.SERVICE in dict_from_server.keys():
                dict_from_server_service_type = dict_from_server[SETTINGS.SERVICE]
                if dict_from_server_service_type in data_objects_dict.keys():
                    data_from_server = data_objects_dict[dict_from_server_service_type](dict_from_server_service_type)
                    data_from_server.setDataFromDict(dict_from_server[SETTINGS.DATA])
                    data_list.append(data_from_server)

        # Find what only the data that each interface needs, then send it to that interface
        for interface in interface_list:
            data_list_for_interface = list(
                filter(lambda data_object: data_object.service in interface.compatible_services.keys(), data_list))
            # print("Update interface list!")
            interface.update(data_list_for_interface)

        # Sleep until we have an appropriate frame time
        while time.time() - frame_start_time <= 1 / fps:
            time.sleep(0.001)


def getInterfaces(settings):
    # TODO: Do check for required settings!
    interface_list = list()
    # default_settings = Defaults()
    # interface_settings = default_settings.getSettingsWithDefaults(settings)

    for interface_settings in settings[SETTINGS.INTERFACE_LIST]:
        if interface_settings[SETTINGS.INTERFACE] == SETTINGS.MATRIX:
            from Interfaces.Matrix import Matrix
            interface_list.append(Matrix(interface_settings))

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.NEOPIXEL:
            from Interfaces.Neopixel import Neopixel
            interface_list.append(Neopixel(interface_settings))

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.FIFTY_FIFTY:
            from Interfaces.FiftyFifty import FiftyFifty
            interface_list.append(FiftyFifty(interface_settings))

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.LOGGER:
            from Interfaces.Logger import Logger
            interface_list.append(Logger(interface_settings))

    if len(interface_list) == 0:
        print("No interfaces detected in config!")
        sys.exit()

    map(lambda interface: interface.ensureImportantPropertiesAreSet(), interface_list)

    return interface_list


class AutobahnTwistedClient:
    def __init__(self, settings):
        self.settings = settings
        self.server_ip = self.settings[SETTINGS.SERVER_IP_ADDRESS]
        # log.startLogging(sys.stdout)

        # TODO: Connect to PixelPi URL
        self.autobahn_factory = MyClientFactory(u"ws://" + self.server_ip + ":9000", self.settings)
        self.autobahn_factory.protocol = MyClientProtocol



    def run(self):
        reactor.connectTCP(self.server_ip, 9000, self.autobahn_factory)
        reactor.run()

        # loop = asyncio.get_event_loop()
        # coro = loop.create_connection(self.autobahn_factory, self.server_ip, 9000)
        # loop.run_until_complete(coro)
        # loop.run_forever()
        #
        # loop.close()


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # Send server some basic details about the device upon connecting
        register_msg = self.factory.settings
        register_msg[NETWORK.COMMAND] = NETWORK.REGISTER_DEVICE

        self.sendMessage(json.dumps(register_msg, ensure_ascii=False).encode('utf8'))

    def onMessage(self, payload, is_binary):
        # print("Message received!")
        if not is_binary:
            msg = json.loads(payload.decode('utf-8'))
            print("Message received!")
            # print(msg)

            # if msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
            #     print("Display command!")
            #     if msg[NETWORK.MODE] == NETWORK.AUDIO:
            #         if self.factory.locked_cmd_queue.full():
            #             old_value_in_queue = self.factory.locked_cmd_queue.get()
            #
            #         self.factory.locked_cmd_queue.put(msg)
            #
            #     elif msg[NETWORK.MODE] == NETWORK.HOME:
            #         # print("Put in display queue")
            #         self.factory.unlocked_cmd_queue.put(msg)
            #
            # elif msg[NETWORK.COMMAND] == NETWORK.REMOVE:
            #     self.factory.unlocked_cmd_queue.put(msg)

            # print("Message going to be added!")

            server_msg_queue.put(msg)

            # print("Item added to queue!")

            # else:
            #     pass
            #     # TODO: Create command not found message
            # self.sendMessage(json.dumps(command_not_found_msg, ensure_ascii=False).encode('utf8'))

    def onClose(self, was_clean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        # server_msg_queue.put()
        sys.exit(0)


class MyClientFactory(WebSocketClientFactory):
    def __init__(self, url, settings):
        WebSocketClientFactory.__init__(self, url)
        # ReconnectingClientFactory.__init__(self)

        self.settings = settings

        self.is_active = True

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal_handler)

    interface_list = getInterfaces(Config.client)
    network_client = AutobahnTwistedClient(Config.client)

    fps = 20

    interface_handler_process = Process(target=runInterfaces, args=(server_msg_queue, interface_list))
    interface_handler_process.start()

    network_client.run()
    interface_handler_process.join()
