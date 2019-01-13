import Keys.Settings as SETTINGS


server = {
    SETTINGS.SERVICE_LIST: [
        {
            SETTINGS.SERVICE: SETTINGS.SPECTRUM_ANALYZER,
            SETTINGS.NO_DISPLAY_TOLERANCE: 1.4
        }
    ]
}

client = {
    SETTINGS.SERVER_IP_ADDRESS: '127.0.0.1',
    SETTINGS.DESCRIPTION: "Raspberry Pi 3b+",
    SETTINGS.INTERFACE_LIST: [
        {
            SETTINGS.INTERFACE: SETTINGS.LOGGER,
            SETTINGS.UNIQUE_IDENTIFIER: "LG01",
            SETTINGS.DESCRIPTION: "Logger to test client"
        },
        # {
        #     SETTINGS.INTERFACE: SETTINGS.MATRIX,
        #     SETTINGS.UNIQUE_IDENTIFIER: "MA01",
        #     SETTINGS.DESCRIPTION: "Matrix by tv",
        #     SETTINGS.HAT: True,
        #     SETTINGS.TIME_ZONE: "US/Eastern"
        #     # SETTINGS.FONTS_LOCATION: /pi/home/...
        # },
    ]
    
##    SETTINGS.NEOPIXEL: [
##        {
##            SETTINGS.UNIQUE_IDENTIFIER: "NP01",
##            SETTINGS.DESCRIPTION: "Neopixel for testing!",
##            SETTINGS.MAIN_PIN: 18,
##            SETTINGS.LED_COUNT: 150,
##            SETTINGS.RGB_ORDER: [SETTINGS.GREEN, SETTINGS.RED, SETTINGS.BLUE]
##        }
##    ],
##    SETTINGS.FIFTY_FIFTY: [
##        {
##            SETTINGS.UNIQUE_IDENTIFIER: "5001",
##            SETTINGS.DESCRIPTION: "FiftyFifty for testing!",
##            SETTINGS.STRIP_TYPE: SETTINGS.STRIP_PRIMARY,
##            SETTINGS.RED_PIN: 18,
##            SETTINGS.GREEN_PIN: 0,
##            SETTINGS.BLUE_PIN: 0,
##        }
##    ]
}



