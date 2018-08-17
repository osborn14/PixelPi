import queue

def init():
    global audio_queue
    audio_queue = queue.Queue(3)

COMMAND = "Command"
DISPLAY = "Display"
MODE = "Mode"
AUDIO = "Audio"
AUDIO_DATA = "Audio Data"
SPECTRUM_AVG = "Spectrum Average"
SPECTRUM_HEIGHTS = "Spectrum Heights"
SPECTRUM_PRIMARY_COLORS = "Spectrumn Primary Colors"
SPECTRUM_SECONDARY_COLORS = "Spectrum Secondary Colors"
AUDIO_DISPLAY_MODE = "Display Modes"
MUSIC_IS_PLAYING = "Music Is Playing"

