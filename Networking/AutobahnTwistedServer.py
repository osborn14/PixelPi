import json, threading, time

from Interfaces.Interface import Interface
from Interfaces.Common.Task import Task
from Networking.Device import Device
# from Database.ClientTaskDatabase import ClientTaskDatabase
# from Networking.AudioServerConnection import AudioServerConnection

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from twisted.internet import reactor
from twisted.python import log

# database = ClientTaskDatabase()


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
        self.autobahn_factory.protocol.broadcast_audio_data(json_message.encode('utf8'))


class MyServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onMessage(self, payload, is_binary):
        print("Message received!")

        if not is_binary:
            msg = json.loads(payload.decode('utf8'))
            print(msg)

            # network_message_dict = {
            #     NETWORK.REGISTER_DEVICE: handleRegister,
            #     NETWORK.DISPLAY: handleDisplay
            # }

            if msg[NETWORK.COMMAND] == NETWORK.REGISTER_DEVICE:
                new_device = Device(self, msg)
                self.factory.authenticated_clients.append(new_device)
                print(len(self.factory.authenticated_clients))

                # First check if the new device is an admin
                if new_device.checkForAdminInterface():
                    # We want to get all non-admin interface jsons
                    non_admin_devices = list(filter(lambda device: False if device.checkForAdminInterface() else True, registered_device_list))
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

            elif msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
                #if SETTINGS.TASK_ID not in msg:
                    # TODO: Move tasks to object
                    # database.addTask(msg[NETWORK.TARGET_INTERFACE_IDENTIFIER], json.dumps(payload.decode('utf8')))
                msg[SETTINGS.TASK_ID] = 1

                for device in self.factory.authenticated_clients:
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
                            
                            no_manual_task_list = list(filter(lambda task: task.on_off_control != NETWORK.MANUAL, target_interface.task_list))

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

            # elif msg['cmd'] == 'VIEW AVAILABLE CLIENTS':
            #     all_devices_dict = {'cmd': 'VIEW AVAILABLE CLIENTS', 'devices': []}
            #     for cd in registered_device_list:
            #         if cd.category != 'AD':
            #             print("Name added!" + cd.name)
            #
            #             device_dict = {'device code': cd.name}
            #             dict(device_dict, **database.viewTasks(cd.name))
            #             all_devices_dict['devices'].append(device_dict)
            #
            #     self.sendMessage(json.dumps(all_devices_dict).encode('utf8'))


                # if msg['cmd'] == 'AUTHENTICATE':
                #     print('un' + msg['username'])
                #     print('pw' + msg['password'])
                #     login_status = database.authenticateUser(msg['username'], msg['password'])
                #     print(str(login_status))
                #     self.sendMessage(json.dumps({'cmd': 'AUTHENTICATE', 'status': str(login_status)}).encode('utf8'))

                ##            elif msg['cmd'] == 'CLEAR':
                ##                removeTask(msg['id'])
                ##                sendJsonToSingleClient(msg)

        # self.factory.broadcast(payload.decode("utf-8"))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    @classmethod
    def broadcast_audio_data(cls, payload):
        for cd in registered_device_list:
            print("Message sent!")
            reactor.callFromThread(cls.sendMessage, cd.client, payload)


class MyServerFactory(WebSocketServerFactory):
    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.authenticated_clients = list()

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        for device in self.authenticated_clients:
            if device.client == client:
                self.authenticated_clients.remove(device)

        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg)
            print("message sent to {}".format(c.peer))


#class BroadcastPreparedServerFactory(BroadcastServerFactory):
    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    # def broadcast(self, msg):
    #     print("broadcasting prepared message '{}' ..".format(msg))
    #     preparedMsg = self.prepareMessage(msg)
    #     for c in self.clients:
    #         c.sendPreparedMessage(preparedMsg)
    #         print("prepared message sent to {}".format(c.peer))