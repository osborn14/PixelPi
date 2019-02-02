import datetime

import Keys.Network as NETWORK
import Keys.Settings as SETTINGS


class Task:
    def __init__(self, settings):
        self.settings = settings
        # TODO: Probably need to search for an object here instead of simply storing a json
        self.task_id = settings[SETTINGS.TASK_ID]
        self.display_effect = settings[NETWORK.DISPLAY_EFFECT]
        # self.on_off_control =

        if self.on_off_control == NETWORK.TIMER:
            self.on_off_control_object = Timer(settings[NETWORK.ON_OFF_CONTROL_DETAILS])

    def getTaskJson(self):
        return self.settings

    def shouldBeActive(self):
        if self.on_off_control == NETWORK.MANUAL:
            return True
        elif self.on_off_control == NETWORK.TIMER:
            return self.on_off_control_object.shouldBeOn()

    def getRgbToDisplay(self):
        NotImplementedError


class Simple(Task):
    def __init__(self, settings):
        super().__init__(settings)
        self.Rgb = list(map(lambda color: int(color), settings[NETWORK.RGB]))

    def getRgbToDisplay(self):
        return self.Rgb


class Trigger:
    def __init__(self, settings):
        pass
        # settings[NETWORK.ON_OFF_CONTROL] =

class Timer():
    def __init__(self, settings):
        super().__init__(self, settings)
        self.start_day = settings[SETTINGS.START_DAY]
        self.start_hour = settings[SETTINGS.START_HOUR]
        self.start_minute = settings[SETTINGS.START_MINUTE]
        self.end_day = settings[SETTINGS.END_DAY]
        self.end_hour = settings[SETTINGS.END_HOUR]
        self.end_minute = settings[SETTINGS.END_MINUTE]
        self.activated = False

    def shouldBeOn(self):
        today = datetime.today()
        starting_datetime = datetime(today.year, today.month, self.start_day, self.start_hour, self.start_minute)
        ending_datetime = datetime(today.year, today.month, self.end_day, self.end_hour, self.end_minute)

        if starting_datetime < today < ending_datetime:
            return True
        else:
            return False