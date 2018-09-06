import json, sys
from Application.Settings.Settings import Settings
import Application.Keys.Network as NETWORK
import Application.Keys.Settings as SETTINGS

from autobahn.asyncio.websocket import WebSocketClientProtocol

settings = Settings()
client_settings = settings.getUniversalClientSettings()
interface_list = settings.getInterfaces()
print("Interfaces: " +  str(len(interface_list)))

class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # Send server some basic details about the device upon connecting
        interface_descriptions = list(map(lambda interface: interface.getInterfaceJson(), interface_list))
        
        print(client_settings)
        register_msg = {
            NETWORK.COMMAND: NETWORK.REGISTER_DEVICE,
            SETTINGS.DEVICE: {
                SETTINGS.DESCRIPTION: client_settings[SETTINGS.DESCRIPTION]
            },
            SETTINGS.INTERFACE_LIST: interface_descriptions
        }
        
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
        
        
