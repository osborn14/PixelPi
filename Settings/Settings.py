import sys

import Keys.Settings as SETTINGS
from Interfaces.Matrix import Matrix


import Settings.Config as Config


class Settings(object):
    # TODO: Settings should be able to be modified from website
    def getServerSettings(self):
        try:

            self.server_settings = Config.server
        except AttributeError:
            print("No server settings found!")
            sys.exit()

        return self.server_settings

    def getUniversalClientSettings(self):
        try:
            self.client_settings = Config.client
        except AttributeError:
            print("No client settings found!")
            sys.exit()

        return self.client_settings



