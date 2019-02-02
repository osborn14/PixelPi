import time, threading, json

import Keys.Settings as SETTINGS
import Settings.Config as Config


from Networking.AutobahnTwistedServer import AutobahnTwistedServer


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
        self.network_server = AutobahnTwistedServer()

    def run(self):
        broadcast_services_thread = threading.Thread(target=self.runBroadcastServices)
        broadcast_services_thread.setDaemon(True)
        broadcast_services_thread.start()

        self.network_server.run()

    def runBroadcastServices(self):
        while True:
            last_updated_dict = dict()
            for broadcast_service in self.broadcast_services_list:
                updated_data = broadcast_service.update()

                if updated_data:
                    broadcast_dict = broadcast_service.getBroadcastDict(updated_data)
                    broadcast_json = json.dumps(broadcast_dict, ensure_ascii=False)
                    self.network_server.broadcast(broadcast_json)

            time.sleep(0.05)

    def getBroadcastServices(self, settings):
        broadcast_services_list = list()

        for service_settings in settings[SETTINGS.SERVICE_LIST]:
            if service_settings[SETTINGS.SERVICE] == SETTINGS.SPECTRUM_ANALYZER:
                from Services.SpectrumAnalyzer import SpectrumAnalyzer
                broadcast_services_list.append(SpectrumAnalyzer(service_settings))

            # if service_settings[SETTINGS.SERVICE] == SETTINGS.WEATHER:
            #     from Services.Weather import Weather
            #

        return broadcast_services_list


if __name__ == "__main__":
    server = Server(Config.server)
    server.run()
