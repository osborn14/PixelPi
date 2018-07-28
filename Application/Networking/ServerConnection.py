import time

from Application.Display import RPiLEDFunctions as led_fx
from Application.Common import AudioData

class AudioServerConnection():
    def __init__(self, settings):
        self.server_ip = settings.SERVER_IP_ADDRESS
        self.port_one = settings.AUDIO_SERVER_PORT_ONE
        self.port_two = settings.AUDIO_SERVER_PORT_TWO
        self.no_display_tolerance = settings.NO_DISPLAY_TOLERANCE

        ## The first server provides us with the audio spectrum analysis, broken into 16 pieces
        self.sock1 = led_fx.connectToServer(self.server_ip, self.port_one)
        
        ## The second server will give us all the main and secondary rgb information, along with display mode
        self.sock2 = led_fx.connectToServer(self.server_ip, self.port_two)
        
        ## lastdisplayedvalue makes sure we don't display any values that are older than what we just displayed
        ## only new values should be displayed
        self.last_displayed_value = 0

        self.start_time = time.time()

    def getAudioServerData(self):
        # Get the values from the first server
        expected_array_list_size1 = 19
        datalist1 = led_fx.receiveAndCleanData(self.sock1, expected_array_list_size1)
        if not datalist1:
            datalist1 = [1] * 18
            self.last_displayed_value = 0
            self.sock1 = led_fx.connectToServer(self.server_ip, self.port_one)
    
        if datalist1[0] > self.last_displayed_value:
            audio_data = AudioData()
            self.last_displayed_value = datalist1[0]
            # Get the values from the second server
            expected_array_list_size2 = 7
            datalist2 = led_fx.receiveAndCleanData(self.sock2, expected_array_list_size2)
            
            if datalist2:
                audio_data.display_mode = datalist2[0]
                audio_data.server_primary_colors = [datalist2[1], datalist2[2], datalist2[3]]
                audio_data.server_secondary_colors = [datalist2[4], datalist2[5], datalist2[6]]
            
            else:
                self.sock2 = led_fx.connectToServer(self.server_ip, self.port_two)

            audio_data.display_mode = datalist2[0]
            audio_data.primary_colors = [datalist2[1], datalist2[2], datalist2[3]]
            audio_data.secondary_colors = [datalist2[4], datalist2[5], datalist2[6]]

            audio_data.spectrum_avg = datalist1[1]
            audio_data.spectrum_heights = led_fx.getDataListtoPrint(audio_data.spectrum_heights, datalist1, 2, 18)

            if audio_data.spectrum_avg < self.SETTINGS_FILE.no_display_tolerance:
                # Remove any small static that the server sends over
                audio_data.spectrum_heights = [1] * 16

                if time.time() - self.start_time > 60:
                    # Has it been 60 seconds with no activity?  If so, note that music is off for now
                    audio_data.music_is_not_playing = True

            else:
                self.start_time = time.time()
                audio_data.music_is_not_playing = False

        return audio_data
            

