import Keys.Settings as SETTINGS

client = {
	SETTINGS.SERVER_IP_ADDRESS: "127.0.0.1",
	SETTINGS.DESCRIPTION: "Raspberry Pi 3b",
	SETTINGS.INTERFACE_LIST: [
		{
			SETTINGS.INTERFACE: SETTINGS.NEOPIXEL,
			SETTINGS.UNIQUE_IDENTIFIER: "NPTS01",
			SETTINGS.MAIN_PIN: 18,
			SETTINGS.LED_COUNT: 50
		}
	]
}
