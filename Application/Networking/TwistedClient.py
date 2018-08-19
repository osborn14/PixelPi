import json
from Application.Settings.Settings import Settings
import Application.Keys.Network as NETWORK

from autobahn.asyncio.websocket import WebSocketClientProtocol

settings = Settings()
interface_list = settings.getInterfaces()

def getInterfaceDict(interface):


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        for interface in interface_list:


        ## Send server some basic details about the device upon connecting
        device_name = settings_file[]
        device_code = settings_file.device_code
        device_type = settings_file.device_type
        device_location = "temp"
        self.sendMessage(json.dumps({'cmd' : 'REGISTER DEVICE', 'device_name':device_name ,'device code': device_code, 'device_type': device_type}).encode('utf8'))


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
                    
                    ## Put the display mode into the proper category
                elif msg['mode'] == 'simple':
                    for m in display_mode_list:
                        if type(m)  == Mode:
                            display_mode_list.remove(m)
                    display_mode_list.append(Mode(prepareArrayforDisplay(msg['rgb array'])))
                elif msg['mode'] == 'timer':
                    display_mode_list.append(Timer(msg['timer day'], msg['timer hour'], msg['timer minute'], prepareArrayforDisplay(msg['rgb array'])))
                
                #display_queue.put(payload)
                #print("Text message received: {0}".format(payload.decode('utf8')))
            #except:
                #print("Server sent invalid json!")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        sys.exit()
        
        
