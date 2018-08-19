import queue


def init():
    global display_queue
    global audio_queue

    audio_queue = queue.Queue(3)
    display_queue = queue.Queue(25)

REGISTER_DEVICE = "Register Device"

COMMAND = "Command"
DISPLAY = "Display"
MODE = "Mode"
AUDIO = "Audio"
AUDIO_DATA = "Audio Data"


