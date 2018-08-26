import Application.Keys.Settings as SETTINGS

server = {
    SETTINGS.AUDIO_SERVER_IP_ADDRESS: '192.168.0.106',
    SETTINGS.AUDIO_SERVER_PORT_ONE: 8080,
    SETTINGS.AUDIO_SERVER_PORT_TWO: 8081,
    SETTINGS.NO_DISPLAY_TOLERANCE: 1.4
}

client = {
    SETTINGS.SERVER_IP_ADDRESS: '127.0.0.1',
    SETTINGS.DESCRIPTION: "Raspsberry Pi 3b+"
}

neopixel = [
    {
        SETTINGS.UNIQUE_IDENTIFIER: "NP01",
        SETTINGS.CODE: "NP",
        SETTINGS.DESCRIPTION: "Neopixel for testing!",
        SETTINGS.MAIN_PIN: 18,
        SETTINGS.LED_COUNT: 150
    }
]
