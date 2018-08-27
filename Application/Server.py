import os, sys, json, threading, time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Application.Settings.Settings import Settings
from Application.Networking.AudioServerConnection import AudioServerConnection
import Application.Keys.Network as NETWORK

from Application.Networking.TwistedServer import BroadcastServerProtocol, BroadcastServerFactory
from autobahn.twisted.websocket import listenWS
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

settings = Settings()
server_settings = settings.getServerSettings()

def broadcastAudioData():
    audio_server_connection = AudioServerConnection(server_settings)
    while(True):
        audio_data = audio_server_connection.getAudioServerData()
        if audio_data and audio_data.music_is_playing:
            msg = dict()
            msg[NETWORK.COMMAND] = NETWORK.DISPLAY
            msg[NETWORK.MODE] = NETWORK.AUDIO
            msg[NETWORK.AUDIO_DATA] = audio_data.getAudioJSON()
            
            #print("Should be printing...")
            
            factory.protocol.broadcast_audio_data(json.dumps(msg, ensure_ascii=False).encode('utf8'))

        time.sleep(.05)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

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
