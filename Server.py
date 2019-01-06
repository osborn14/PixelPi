import time, json, threading

import Keys.Settings as SETTINGS
import Keys.Network as NETWORK
import Settings.Config as Config

from Audio import SpectrumAnalyzer
from Networking.AudioServerConnection import AudioServerConnection
from Networking.Server import BroadcastServerFactory, BroadcastServerProtocol

from autobahn.twisted.websocket import listenWS
from twisted.internet import reactor
from twisted.web.server import File, Site


def gatherServer():
    try:
        server_settings = Config.server

    except NameError:
        print("No server detected...")
        return None

    return Server(server_settings)


class Server:
    def __init__(self, settings):
        self.settings = settings
        self.broadcast_services_list = self.getBroadcastServices(settings)

        ServerFactory = BroadcastServerFactory
        self.twisted_factory = ServerFactory("ws://127.0.0.1:9000")
        self.twisted_factory.protocol = BroadcastServerProtocol

    def run(self):
        connection_to_audio_server_thread = threading.Thread(target=self.runBroadcastServices)
        connection_to_audio_server_thread.setDaemon(True)
        connection_to_audio_server_thread.start()

        listenWS(self.twisted_factory)

        webdir = File(".")
        web = Site(webdir)
        print("Starting server...")

        reactor.run(installSignalHandlers=False)

    def runBroadcastServices(self):
        if len(self.broadcast_service_list) > 0:
            while True:
                for broadcast_service in self.broadcast_service_list:
                    updated_data = broadcast_service.update()

                    if updated_data:
                        broadcast_json = broadcast_service.getBroadcastJson(updated_data)
                        self.twisted_factory.protocol.broadcast_audio_data(broadcast_json.encode('utf8'))

                time.sleep(.05)

    def getBroadcastServices(self, settings):
        broadcast_service_list = list()

        for service in settings[SETTINGS.SERVICE_LIST]:
            if service[SETTINGS.SERVICE] == SETTINGS.SPECTRUM_ANALYZER:
                broadcast_service_list.append(SpectrumAnalyzer())

        return broadcast_service_list


if __name__ == "__main__":
    server = Server(Config.server)
    server.run()
