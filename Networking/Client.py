import json, sys, time, threading, queue
import Keys.Network as NETWORK
import Keys.Settings as SETTINGS

from Audio.AudioData import AudioData
from Interfaces.Common.Task import Task, Simple

from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.asyncio.websocket import WebSocketClientFactory, WebSocketClientProtocol

NETWORK.init()


global audio_queue, display_queue, remove_queue
audio_queue = queue.Queue(3)
display_queue = remove_queue = queue.Queue(25)



class MyClientProtocol(WebSocketClientProtocol):
    client_settings = dict()
    interface_list = list()

    @classmethod
    def setClassVariables(cls, client_settings, interface_list):
        cls.client_settings = client_settings
        cls.interface_list = interface_list

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # Send server some basic details about the device upon connecting
        #interface_descriptions = list(map(lambda interface: interface.getInterfaceJson(), interface_list))
        
        register_msg = self.client_settings
        register_msg[NETWORK.COMMAND] = NETWORK.REGISTER_DEVICE
##        register_msg = {
##            NETWORK.COMMAND: NETWORK.REGISTER_DEVICE,
##            SETTINGS.DEVICE: {
##                SETTINGS.DESCRIPTION: client_settings[SETTINGS.DESCRIPTION]
##            },
##            SETTINGS.INTERFACE_LIST: interface_descriptions
            
##        }
        
        print(register_msg)

        self.sendMessage(json.dumps(register_msg, ensure_ascii=False).encode('utf8'))

    def onMessage(self, payload, isBinary):
        #print("Message received!")
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            msg = json.loads(payload.decode('utf-8'))
            print(msg)

            if msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
                print("Display command!")
                if msg[NETWORK.MODE] == NETWORK.AUDIO:
                    if NETWORK.audio_queue.full():
                        old_value_in_queue = NETWORK.audio_queue.get()
                        
                    NETWORK.audio_queue.put(msg)

                elif msg[NETWORK.MODE] == NETWORK.HOME:
                    print("Put in display queue")
                    NETWORK.display_queue.put(msg)
                    
            elif msg[NETWORK.COMMAND] == NETWORK.REMOVE:
                NETWORK.remove_queue.put(msg)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        #sys.exit()
        
        
class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = MyClientProtocol

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)