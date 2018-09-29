import json, sys, time
import Keys.Network as NETWORK
import Keys.Settings as SETTINGS

from Audio.AudioData import AudioData

from autobahn.asyncio.websocket import WebSocketClientFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol

global client_settings
global interface_list

class Client():
    def __init__(self, temp_client_settings, temp_interface_list):



        client_settings = temp_client_settings
        interface_list = temp_interface_list
                
        try:
            import asyncio
        except ImportError:
            # Trollius >= 0.3 was renamed
            import trollius as asyncio

        factory = WebSocketClientFactory(u"ws://" + client_settings[SETTINGS.SERVER_IP_ADDRESS] + ":" + str(9000))
        factory.protocol = MyClientProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, client_settings[SETTINGS.SERVER_IP_ADDRESS], 9000)

        while True:
            loop.run_until_complete(coro)

            try:
                loop.run_forever()
            except:
                print("Connection to server lost!")
            finally:
                loop.close()

            time.sleep(1)

    def displayLights(self):
        while True:
            print("In while loop")
            if not NETWORK.remove_queue.empty():
                print("Retrieved from remove queue!")
                self.processServerJson(NETWORK.remove_queue.get())

            elif not NETWORK.display_queue.empty():
                print("Retrieved from display queue!")
                self.processServerJson(NETWORK.display_queue.get())

            elif not NETWORK.audio_queue.empty():
                print("Audio [playing")
                last_played_time = time.time()
                audio_data = AudioData()

                while True:
                    if not NETWORK.audio_queue.empty():
                        last_played_time = time.time()

                        audio_dict = NETWORK.audio_queue.get()
                        audio_data.setAudioDataFromJSON(audio_dict[NETWORK.AUDIO_DATA])

                    elif time.time() - last_played_time >= 45:
                        break;

                    else:
                        audio_data.setSpectrumToZero()

                    for interface in interface_list:
                        interface.displayAudioLights(audio_data)

            else:
                for interface in interface_list:
                    interface.displayNormalLights()

                time.sleep(.1)

    def processServerJson(self, msg):
        print("Processing server json!")
        for interface in interface_list:
            if interface.unique_identifier == msg[SETTINGS.UNIQUE_IDENTIFIER]:
                if msg[NETWORK.COMMAND] == NETWORK.DISPLAY:
                    if msg[NETWORK.DISPLAY_EFFECT] == NETWORK.SIMPLE:
                        interface.task_list.append(Simple(msg))

                if msg[NETWORK.COMMAND] == NETWORK.REMOVE:
                    for remove_id in msg[NETWORK.REMOVE_LIST]:
                        interface.task_list = list(filter(lambda task: task.task_id != remove_id, interface.task_list))

        print(msg)


class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        # Send server some basic details about the device upon connecting
        #interface_descriptions = list(map(lambda interface: interface.getInterfaceJson(), interface_list))
        
        print(client_settings)
        register_msg = client_settings
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
        
        
