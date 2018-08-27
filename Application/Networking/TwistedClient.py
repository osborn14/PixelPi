import json
from Application.Settings.Settings import Settings
import Application.Keys.Network as NETWORK
import Application.Keys.Settings as SETTINGS

from autobahn.asyncio.websocket import WebSocketClientProtocol

settings = Settings()
client_settings = settings.getUniversalClientSettings()
interface_list = settings.getInterfaces()

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
            #try:
            #print(payload.decode('utf-8'))
            msg = json.loads(payload.decode('utf-8'))
                ## Consider ids for removing orders
                ## Or, send a remove all command and send all again

            if msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
                if msg[NETWORK.MODE] == NETWORK.AUDIO:                    
                    if NETWORK.audio_queue.full():
                        old_value_in_queue = NETWORK.audio_queue.get()
                        
                    NETWORK.audio_queue.put(msg)

                elif msg[NETWORK.MODE] == NETWORK.HOME:
                    NETWORK.display_queue.put(msg)




                #     for m in display_mode_list:
                #         if type(m)  == Mode:
                #             display_mode_list.remove(m)
                #     display_mode_list.append(Mode(prepareArrayforDisplay(msg['rgb array'])))
                # elif msg['mode'] == 'timer':
                #     display_mode_list.append(Timer(msg['timer day'], msg['timer hour'], msg['timer minute'], prepareArrayforDisplay(msg['rgb array'])))
                
                #display_queue.put(payload)
                #print("Text message received: {0}".format(payload.decode('utf8')))
            #except:
                #print("Server sent invalid json!")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        sys.exit()
        
        
