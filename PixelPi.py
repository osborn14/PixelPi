import sys, os, threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Server import gatherServer
from Client import gatherClient


# def signal_handler(signal, frame):
#     for interface in interface_list:
#         interface.displayDefaultLights()
#
#     sys.exit(0)

class PixelPi:
    def __init__(self, args):
        self.service_list = list()

        server = gatherServer()
        if server:
            self.service_list.append(server)

        client = gatherClient()
        if client:
            self.service_list.append(client)

    def run(self):
        thread_list = list()

        for service in self.service_list:
            service_thread = threading.Thread(target=service.run)
            service_thread.setDaemon(True)
            service_thread.start()

            thread_list.append(service_thread)

        for thread in thread_list:
            thread.join()


if __name__ == "__main__":
    pixel_pi = PixelPi()
    pixel_pi.run()
