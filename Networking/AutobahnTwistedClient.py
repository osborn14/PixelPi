import json, sys, queue
import Keys.Network as NETWORK

import Keys.Settings as SETTINGS

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor


class AutobahnTwistedClient:
    def __init__(self, settings):
        self.settings = settings

        # log.startLogging(sys.stdout)

        # TODO: Connect to PixelPi URL
        self.autobahn_factory = MyClientFactory(u"ws://" + self.settings[SETTINGS.SERVER_IP_ADDRESS] + ":9000", settings)
        self.autobahn_factory.protocol = MyClientProtocol

    def run(self):
        reactor.connectTCP(self.settings[SETTINGS.SERVER_IP_ADDRESS], 9000, self.autobahn_factory)
        reactor.run()


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # Send server some basic details about the device upon connecting
        register_msg = self.factory.settings
        register_msg[NETWORK.COMMAND] = NETWORK.REGISTER_DEVICE

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
                    if self.factory.audio_queue.full():
                        old_value_in_queue = self.factory.audio_queue.get()
                        
                    self.factory.audio_queue.put(msg)

                elif msg[NETWORK.MODE] == NETWORK.HOME:
                    # print("Put in display queue")
                    self.factory.display_queue.put(msg)
                    
            elif msg[NETWORK.COMMAND] == NETWORK.REMOVE:
                self.factory.remove_queue.put(msg)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.is_active = False
        sys.exit(0)
        
        
class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    def __init__(self, url, settings):
        WebSocketClientFactory.__init__(self, url)
        ReconnectingClientFactory.__init__(self)

        self.settings = settings
        self.is_active = True

        self.audio_queue = queue.Queue(2)
        self.display_queue = self.remove_queue = queue.Queue(25)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
