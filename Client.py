

import os, sys, json, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Keys.Network as NETWORK

from multiprocessing import Process, Queue

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

    from Interfaces.Interface import InterfaceRunner

    for interface_settings in settings[SETTINGS.INTERFACE_LIST]:
        interface_runner = InterfaceRunner()
        interface_runner.setInterface(interface_settings)

        if interface_runner.interface is not None:
            interface_list.append(interface_runner)

    if len(interface_list) == 0:
        print("No interfaces detected in config!")
        sys.exit()

    map(lambda interface: interface.ensureImportantPropertiesAreSet(), interface_list)

    return interface_list


def getServices(settings, services_queue):
    # TODO: Do check for required settings!
    service_list = list()
    # default_settings = Defaults()
    # interface_settings = default_settings.getSettingsWithDefaults(settings)

    for interface_settings in settings[SETTINGS.INTERFACE_LIST]:
        device_unique_name = interface_settings[SETTINGS.UNIQUE_IDENTIFIER]

        if interface_settings[SETTINGS.INTERFACE] == SETTINGS.NEOPIXEL or interface_settings[SETTINGS.INTERFACE] == SETTINGS.FIFTY_FIFTY or interface_settings[SETTINGS.INTERFACE] == SETTINGS.LOGGER:
            from Services.HomeKitRGBLight import HomeKitDeviceRunner
            service_list.append(HomeKitDeviceRunner(interface_settings, services_queue))

    if len(service_list) == 0:
        print("No interfaces detected in config!")
        sys.exit()

    map(lambda interface: interface.ensureImportantPropertiesAreSet(), interface_list)

    return service_list


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal_handler)

    service_queue = Queue()

    interface_runner_process_list = getInterfaces(Config.client)
    service_process_list = getServices(Config.client, service_queue)

    # network_client = AutobahnTwistedClient(Config.client)

    single_interface_process = interface_runner_process_list[0]
    single_interface_process.run()

    # for interface_runner in interface_runner_process_list:
    #     interface_runner.interface.run()

    for service in service_process_list:
        service.run()

    # while True:
    #     if not service_queue.empty():
    #         service_data = service_queue.get()
    #
    #         for interface_runner in interface_runner_process_list:
    #             if interface_runner.compatible_services
    #
    # for interface in interface_process_list:
    #     interface.join()
    #
    # for service in service_process_list:
    #     service.join()



    fps = 20

    #interface_handler_process = Process(target=runInterfaces, args=(server_msg_queue, interface_list))
    #interface_handler_process.start()

    # network_client.run()
    # interface_handler_process.join()
