from Interfaces.Interface import Interface

import Keys.Settings as SETTINGS


class Device:
    def __init__(self, client, device_dict):
        print(device_dict)
        self.client = client
        self.description = device_dict[SETTINGS.DESCRIPTION]
        self.interface_list = list(
            map(lambda interface_dict: Interface(interface_dict), device_dict[SETTINGS.INTERFACE_LIST]))

    def getDeviceInfo(self):
        interface_json_list = list(map(lambda interface: interface.getInterfaceJson(), self.interface_list))

        device_dict = {
            SETTINGS.DESCRIPTION: self.description,
            SETTINGS.INTERFACE_LIST: interface_json_list
        }

        return device_dict

    def checkForAdminInterface(self):
        for interface in self.interface_list:
            if interface.code == SETTINGS.CODE_ADMIN:
                print(self.description)
                return interface.unique_identifier

        return None

    def checkForTargetInterface(self, target_identifier):
        for interface in self.interface_list:
            if interface.unique_identifier == target_identifier:
                return interface.unique_identifier

        return None

    def updateInterfaceTaskList(self, interface_id, task_list):
        for interface in self.interface_list:
            if interface.unique_identifier == interface_id:
                interface.task_list = task_list
