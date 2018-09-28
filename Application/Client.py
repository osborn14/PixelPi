import threading, time, sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Application.Settings.Settings as Settings
from Application.Networking.TwistedClient import TwistedClient
from Application.Audio.AudioData import AudioData
from Application.Interfaces.Common.Task import Task, Simple
import Application.Keys.Settings as SETTINGS
import Application.Keys.Network as NETWORK

from autobahn.asyncio.websocket import WebSocketClientFactory

# Create our settings file as a global variable
NETWORK.init()

settings = Settings.Settings()
client_settings = settings.getUniversalClientSettings()
interface_list = settings.getInterfaces()

def signal_handler(signal, frame):
    for interface in interface_list:
        interface.displayDefaultLights()

    sys.exit(0)

# def opt_parse():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-c', action='store_true', help='clear the display on exit')
#     args = parser.parse_args()
#     if args.c:
#         signal.signal(signal.SIGINT, signal_handler)
#

def processServerJson(msg):
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

def displayLights():
    while True:
        print("In while loop")
        if not NETWORK.remove_queue.empty():
            print("Retrieved from remove queue!")
            processServerJson(NETWORK.remove_queue.get())
        
        elif not NETWORK.display_queue.empty():
            print("Retrieved from display queue!")
            processServerJson(NETWORK.display_queue.get())

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


if __name__ == '__main__':
    
    # Process arguments
    # opt_parse()
    # display_mode_list = list()
        
    
    connection_to_audio_server_thread = threading.Thread(target=displayLights)
    connection_to_audio_server_thread.setDaemon(True)
    connection_to_audio_server_thread.start()
    
    twisted_client = TwistedClient(client_settings, interface_list)





