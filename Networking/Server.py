import json, threading, time

from Interfaces.Interface import Interface
from Interfaces.Common.Task import Task
#from Database.ClientTaskDatabase import ClientTaskDatabase
from Networking.AudioServerConnection import AudioServerConnection

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import File, Site

#database = ClientTaskDatabase()

registered_device_list = list()
temp_neopixel_client = None



class Device():
    def __init__(self, client, device_dict):
        self.client = client
        self.description = device_dict[SETTINGS.DEVICE][SETTINGS.DESCRIPTION]
        self.interface_list = list(map(lambda interface_dict: Interface(interface_dict), device_dict[SETTINGS.INTERFACE_LIST]))

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



class BroadcastServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))
        

    def onMessage(self, payload, isBinary):
        print("Message received!")

        if not isBinary:
            msg = json.loads(payload.decode('utf8'))
            print(msg)

            if msg[NETWORK.COMMAND] == NETWORK.REGISTER_DEVICE:
                new_device = Device(self, msg)
                registered_device_list.append(new_device)
                print(len(registered_device_list))

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

                for device in registered_device_list:
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


class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        #self.tickcount = 0
        #self.tick()

    #def tick(self):
        #self.tickcount += 1

    ##        self.broadcast("tick %d from server" % self.tickcount)
    ##        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        for device in registered_device_list:
            if device.client == client:
                registered_device_list.remove(device)

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