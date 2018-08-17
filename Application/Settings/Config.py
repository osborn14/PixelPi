import Application.Keys.Settings as KEY

server = {
    KEY.AUDIO_SERVER_IP_ADDRESS: '192.168.0.106',
    KEY.AUDIO_SERVER_PORT_ONE: 8080,
    KEY.AUDIO_SERVER_PORT_TWO: 8081,
    KEY.NO_DISPLAY_TOLERANCE: 1.4
}

client = {
    KEY.SERVER_IP_ADDRESS: '127.0.0.1',
    KEY.NO_DISPLAY_TOLERANCE: 1.4
    
}
neopixel = [
    {
        KEY.MAIN_PIN: 18,
        KEY.LED_COUNT: 150
    }
]
