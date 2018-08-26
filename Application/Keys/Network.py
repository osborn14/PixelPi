import queue


def init():
    global display_queue
    global audio_queue

    audio_queue = queue.Queue(3)
    display_queue = queue.Queue(25)

REGISTER_DEVICE = "Register Device"
TARGET_INTERFACE_IDENTIFIER = "Targer Interface Identifier"
COMMAND = "Command"
MODE = "Mode"
UPDATE = "Update"
DISPLAY = "Display"
DISPLAY_EFFECT = "Display Effect"
ON_OFF_CONTROL = "On Off Control"
ON_OFF_CONTROL_DETAILS = "On Off Control Details"
MANUAL = "Manual"
TIMER = "Timer"
HOME = "HOME"
AUDIO = "Audio"
AUDIO_DATA = "Audio Data"


