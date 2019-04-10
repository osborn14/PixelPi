import sys, time

from multiprocessing import Process, Queue

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS


class InterfaceRunner:
    def __init__(self):
        self.interface_queue = Queue()
        self.interface = None
        self.compatible_services = None

    def setInterface(self, interface_settings):
        self.interface_settings = interface_settings
        self.unique_identifier = interface_settings[SETTINGS.UNIQUE_IDENTIFIER]

        if interface_settings[SETTINGS.INTERFACE] == SETTINGS.MATRIX:
            from Interfaces.Matrix import Matrix
            interface_class = Matrix

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.NEOPIXEL:
            from Interfaces.Neopixel import Neopixel
            interface_class = Neopixel

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.FIFTY_FIFTY:
            from Interfaces.FiftyFifty import FiftyFifty
            interface_class = FiftyFifty

        elif interface_settings[SETTINGS.INTERFACE] == SETTINGS.LOGGER:
            from Interfaces.Logger import Logger
            interface_class = Logger

        else:
            print("Invalid interface provided!")

        self.interface = interface_class(interface_settings, self.interface_queue)
        # self.compatible_services = interface_class.compatible_services

    def run(self):
        self.interface.start()


class Interface(Process):
    def __init__(self, settings, out_queue):
        super(Interface, self).__init__()
        self.settings = settings
        self.out_queue = out_queue
        self.unique_identifier = settings[SETTINGS.UNIQUE_IDENTIFIER]
        self.code = "NA"
        self.description = settings[SETTINGS.DESCRIPTION]
        self.display_task = None
        self.data_object_list = list()
        # self.unprocessed_data_list = list()
        self.last_locked_data = None

        # Must be defined in child classes!
        self.compatible_services = None

    def ensureImportantPropertiesAreSet(self):
        try:
            self.compatible_services
        except NameError:
            "Interface object variable: 'compatible_services' not set! Please set to a valid dictionary!"
            sys.exit()

    def run(self):
        while True:
            new_data_list = list()
            while not self.out_queue.empty():
                new_data_list.append(self.out_queue.get())

            for new_data_object in new_data_list:
                if new_data_object.must_be_singular:
                    latest_similar_data_object = new_data_object
                    for data_object in self.data_object_list:
                        if new_data_object.service == data_object.service:
                            if data_object.creation_time >= new_data_object.creation_time:
                                latest_similar_data_object = data_object
                        self.data_object_list.remove(data_object)

                    self.data_object_list.append(latest_similar_data_object)

                else:
                    self.unprocessed_data_list.append(new_data_object)

            # Process locked data_objects first
            for data_object in self.data_object_list:
                if data_object.locked:
                    current_time = time.time()

                    if current_time - data_object.last_played_time >= 30:
                        self.data_object_list.remove(data_object)
                    elif current_time - data_object.last_played_time >= 0.5:
                        data_object.setToDefaults()
                        data_object.active = True

                    self.compatible_services[data_object.service](data_object)
                    data_object.active = False
                    return

            for data_object in self.data_object_list:
                print()
                pass

            time.sleep(0.05)

        # TODO: Calculate avg server audio message to use for set spectrum avg to zero
        # if self.last_priority_data and self.last_priority_data.active:
        #     self.last_priority_data.last_played_time = current_time


        # if self.last_priority_data and self.last_priority_data.active:

        # else:
        #     if len(self.unprocessed_data_list) > 0:
        #         self.updateDataList()
        #         self.processDataList()
        #
        #     self.runDefaults()

    def processDataList(self):
        for unprocessed_data_object in self.unprocessed_data_list:
            if unprocessed_data_object.must_be_singular:
                latest_singular_data_object = max(self.data_object_list, key=lambda data_object: data_object.creation_time)

                if latest_singular_data_object == unprocessed_data_object:
                    for data_object in self.data_object_list:
                        if data_object.service == unprocessed_data_object.service:
                            self.data_object_list.remove(data_object)

                    self.data_object_list.append(latest_singular_data_object)

            self.unprocessed_data_list.remove(unprocessed_data_object)

    def updateDataList(self):
        pass

    def getInterfaceJson(self):
        data_object_list = list(map(lambda task: task.getTaskJson(), self.data_object_list))

        interface_settings_dict = self.settings
        interface_settings_dict[SETTINGS.TASK_LIST] = data_object_list

        return interface_settings_dict

    def checkForTaskToDisplay(self):
        # Manual tasks always take priority over automatic tasks
        for task in self.data_object_list:
            if task.on_off_control == NETWORK.MANUAL:
                self.display_task = task
                return True

        for task in self.data_object_list:
            if task.shouldBeActive():
                self.display_task = task
                return True

        self.display_task = None
        return False

    def getRgbToDisplay(self):
        if self.checkForTaskToDisplay():
            return self.display_task.getRgbToDisplay()
        else:
            return [0, 0, 0]
    
    #def getDisplayTask(self):
