import json

from Interfaces.Common.Task import Task
from Networking.Device import Device

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from twisted.internet import reactor


class AutobahnTwistedServer:
    def __init__(self):
        server_factory = MyServerFactory

        # TODO: Create static URL
        self.autobahn_factory = server_factory("ws://127.0.0.1:9000")
        self.autobahn_factory.protocol = MyServerProtocol

    def run(self):
        reactor.listenTCP(9000, self.autobahn_factory)
        reactor.run()

    def broadcast(self, json_message):
        self.autobahn_factory.broadcast(json_message.encode('utf8'))


class MyServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onMessage(self, payload, is_binary):
        print("Message received!")

        if not is_binary:
            network_message_dict = {
                NETWORK.REGISTER_DEVICE: self.handleRegister,
                NETWORK.DISPLAY: self.handleDisplay
            }

            msg = json.loads(payload.decode('utf8'))
            network_message_dict[msg[NETWORK.COMMAND]](msg)

            # elif msg['cmd'] == 'VIEW AVAILABLE CLIENTS':
            #     all_devices_dict = {'cmd': 'VIEW AVAILABLE CLIENTS', 'devices': []}
            #     for cd in self.authenticated_devices:
            #         if cd.category != 'AD':
            #             print("Name added!" + cd.name)
            #
            #             device_dict = {'device code': cd.name}
            #             dict(device_dict, **database.viewTasks(cd.name))
            #             all_devices_dict['devices'].append(device_dict)
            #
            #     self.sendMessage(json.dumps(all_devices_dict).encode('utf8'))

    def handleRegister(self, msg):
        new_device = Device(self, msg)
        self.factory.authenticated_devices.append(new_device)
        print(len(self.factory.authenticated_devices))

        # First check if the new device is an admin
        if new_device.checkForAdminInterface():
            # We want to get all non-admin interface jsons
            non_admin_devices = list(
                filter(lambda device: False if device.checkForAdminInterface() else True, self.authenticated_devices))
            non_admin_devices_dicts = list(map(lambda device: device.getDeviceInfo(), non_admin_devices))

            dict_describing_devices = {
                NETWORK.COMMAND: NETWORK.UPDATE,
                SETTINGS.DEVICE_LIST: non_admin_devices_dicts
            }

            print(dict_describing_devices)
            self.sendMessage(json.dumps(dict_describing_devices, ensure_ascii=False).encode('utf8'))
        else:
            # Notify admin of new user here
            print("New user joined!")

    def handleDisplay(self, msg):
        # if SETTINGS.TASK_ID not in msg:
        # TODO: Move tasks to object
        # database.addTask(msg[NETWORK.TARGET_INTERFACE_IDENTIFIER], json.dumps(payload.decode('utf8')))
        msg[SETTINGS.TASK_ID] = 1

        for device in self.factory.authenticated_devices:
            target_interface_id = msg[SETTINGS.UNIQUE_IDENTIFIER]

            if device.checkForTargetInterface(target_interface_id):
                if msg[NETWORK.ON_OFF_CONTROL] == NETWORK.MANUAL:
                    # Get me a single interface that has the appropriate interface id
                    target_interface = next(
                        filter(lambda interface: interface.unique_identifier == target_interface_id,
                               device.interface_list), None)

                    # Find all manual tasks associated with the interface
                    manual_task_list = list(filter(lambda task: task.on_off_control == NETWORK.MANUAL,
                                                   target_interface.task_list))

                    # Interfaces can only have one manual task at a time. Remove any other old ones
                    if len(manual_task_list) > 0:
                        remove_list = list(map(lambda task: task.task_id, manual_task_list))
                        remove_task_command = {
                            NETWORK.COMMAND: NETWORK.REMOVE,
                            SETTINGS.UNIQUE_IDENTIFIER: target_interface.unique_identifier,
                            NETWORK.REMOVE_LIST: remove_list
                        }

                        device.client.sendMessage(json.dumps(remove_task_command, ensure_ascii=False).encode('utf8'))

                    no_manual_task_list = list(
                        filter(lambda task: task.on_off_control != NETWORK.MANUAL, target_interface.task_list))

                    if no_manual_task_list:
                        task_list = no_manual_task_list.append(Task(msg))
                    else:
                        task_list = [Task(msg)]

                    print("New task list", task_list)
                    device.updateInterfaceTaskList(target_interface.unique_identifier, task_list)

                msg[NETWORK.MODE] = NETWORK.HOME
                print(device.client)
                device.client.sendMessage(json.dumps(msg, ensure_ascii=False).encode('utf8'))
                print("Message sent!", msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class MyServerFactory(WebSocketServerFactory):
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.authenticated_devices = list()

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        for device in self.authenticated_devices:
            if device.client == client:
                self.authenticated_devices.remove(device)

        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        # print("broadcasting message '{}' ..".format(msg))
        for device in self.authenticated_devices:
            device.client.sendMessage(msg)
            print("message sent to {}".format(device.client.peer))
