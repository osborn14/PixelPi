import sys, json, threading, time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Application.Settings import Settings
from Application.Database.ServerMySQL import DatabaseConnection
from Application.Networking.AudioServerConnection import AudioServerConnection
from Application.Common.AudioData import AudioData
import Application.Common.NetworkCommands as NETWORK

from Application.Networking.TwistedServer import BroadcastServerProtocol, BroadcastServerFactory

settings = Settings()
server_settings = settings.getServerSettings()

class Device():
    def __init__(self, category, name, client, description):
        self.category = category;
        self.name = name
        self.client = client
        self.description = description


def broadcastAudioData():
    audio_server_connection = AudioServerConnection(server_settings)
    while(True):
        audio_data = audio_server_connection.getAudioServerData()
        if audio_data.music_is_playing:
            for cd in connected_device_list:
                msg = dict()
                msg[NETWORK.CMD] = NETWORK.DISPLAY
                msg[NETWORK.MODE] = NETWORK.AUDIO
                msg[NETWORK.AUDIO_DATA] = audio_data.getAudioJSON()

                cd.client.sendMessage(json.dumps(msg).encode('utf8'))

        time.sleep(.05)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False
        
#
    database_connection = DatabaseConnection()

    connected_device_list = list()
        
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory("ws://127.0.0.1:9000")

    factory.protocol = BroadcastServerProtocol
    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    print("Starting...")

    connection_to_audio_server_thread = threading.Thread(target=broadcastAudioData)
    connection_to_audio_server_thread.setDaemon(True)
    connection_to_audio_server_thread.start()

    reactor.run()
