import Application.Keys.Network as NETWORK
import Application.Keys.Settings as SETTINGS


class Interface():
    def __init__(self, settings):
        self.settings = settings
        self.unique_identifier = settings[SETTINGS.UNIQUE_IDENTIFIER]
        self.code = settings[SETTINGS.CODE]
        self.description = settings[SETTINGS.DESCRIPTION]
        self.display_task = None
        self.task_list = list()

    def getInterfaceJson(self):
        task_list = list(map(lambda task: task.getTaskJson(), self.task_list))

        interface_settings_dict = self.settings
        interface_settings_dict[SETTINGS.TASK_LIST] = task_list

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

        self.display_task = None
        return False

    def getRgbToDisplay(self):
        if self.checkForTaskToDisplay():
            return self.display_task.getRgbToDisplay()
        else:
            return [0, 0, 0]
    
    #def getDisplayTask(self):

    def displayAudioLights(self):
        raise NotImplementedError

    def displayNormalLights(self):
        raise NotImplementedError