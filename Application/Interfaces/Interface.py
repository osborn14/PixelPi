import Application.Keys.Network as NETWORK
import Application.Keys.Settings as SETTINGS


class Interface():
    def __init__(self, settings):
        self.unique_identifier = settings[SETTINGS.UNIQUE_IDENTIFIER]
        # TODO: Code shouldn't be needed on clients end because of config
        self.code = settings[SETTINGS.CODE]
        self.description = settings[SETTINGS.DESCRIPTION]
        self.display_task = None
        self.task_list = list()

    def getInterfaceJson(self):
        task_dict = list(map(lambda task: task.shouldBeActive, self.task_list))

        interface_settings_dict = {
            SETTINGS.UNIQUE_IDENTIFIER: self.unique_identifier,
            SETTINGS.CODE: self.code,
            SETTINGS.DESCRIPTION: self.description,
            SETTINGS.TASK_LIST: task_dict
        }

        return interface_settings_dict

    def checkForTaskToDisplay(self):
        # Manual tasks always take priority over automatic tasks
        for task in self.task_list:
            if task.on_off_control == NETWORK.MANUAL:
                self.display_task = task
                return True

        for task in self.task_list:
            if task.shouldBeActive():
                self.display_task = task
                return True

        return False
    
    #def getDisplayTask(self):

    def displayAudioLights(self):
        raise NotImplementedError

    def displayHomeLights(self):
        raise NotImplementedError