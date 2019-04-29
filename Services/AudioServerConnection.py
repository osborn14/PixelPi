import time, socket, threading

import Keys.Settings as KEY
from Data.AudioData import AudioData


class AudioServerConnection:
    def __init__(self, settings, queue):
        self.server_ip = settings[KEY.AUDIO_SERVER_IP_ADDRESS]
        self.port_one = settings[KEY.AUDIO_SERVER_PORT_ONE]
        self.port_two = settings[KEY.AUDIO_SERVER_PORT_TWO]
        self.no_display_tolerance = settings[KEY.NO_DISPLAY_TOLERANCE]
        self.queue = queue
        
        self.sock_one = None
        self.sock_two = None

        self.music_is_playing = False
        self.music_played_counter = 0

        # lastdisplayedvalue makes sure we don't display any values that are older than what we just displayed
        # only new values should be displayed
        self.last_displayed_value = 0

        self.start_time = time.time()

    def start(self):
        # The first server provides us with the audio spectrum analysis, broken into 16 pieces
        self.sock_one = self.connectToServer(self.server_ip, self.port_one)

        # The second server will give us all the main and secondary rgb information, along with display mode
        self.sock_two = self.connectToServer(self.server_ip, self.port_two)
        
        while True:
            # Get the values from the first server
            expected_array_list_size1 = 19
            data_list_one = self.receiveAndCleanData(self.sock_one, expected_array_list_size1)
            if not data_list_one:
                data_list_one = [0] * 17
                self.last_displayed_value = 0
                self.sock_one = self.connectToServer(self.server_ip, self.port_one)
        
            if data_list_one[0] > self.last_displayed_value:
                audio_data = AudioData()
                self.last_displayed_value = data_list_one[0]
                # Get the values from the second server
                expected_array_list_size2 = 7
                data_list_two = self.receiveAndCleanData(self.sock_two, expected_array_list_size2)
                
                if data_list_two:
                    audio_data.display_mode = data_list_two[0]
                    audio_data.server_primary_colors = [data_list_two[1], data_list_two[2], data_list_two[3]]
                    audio_data.server_secondary_colors = [data_list_two[4], data_list_two[5], data_list_two[6]]
                
                else:
                    self.sock_two = self.connectToServer(self.server_ip, self.port_two)
    
                # audio_data.display_mode = data_list_two[0]
                # audio_data.primary_colors = [data_list_two[1], data_list_two[2], data_list_two[3]]
                # audio_data.secondary_colors = [data_list_two[4], data_list_two[5], data_list_two[6]]
                
                #print(data_list_one)
                
                audio_data.spectrum_heights = data_list_one[1:17]
                audio_data.spectrum_avg = sum(audio_data.spectrum_heights) / len(audio_data.spectrum_heights)
                
                if audio_data.spectrum_avg < self.no_display_tolerance:
                    # Remove any small static that the server sends over
                    audio_data.spectrum_heights = [1] * 16
    
                    if time.time() - self.start_time > 60:
                        # Has it been 60 seconds with no activity?  If so, note that music is off for now
                        self.music_is_playing = False
                        self.music_played_counter = 0
    
                else:
                    self.start_time = time.time()
                    self.music_is_playing = True

                if self.music_is_playing:
                    self.queue.put(audio_data)

            time.sleep(0.01)

    def connectToServer(self, ip, port):
        try:
            sock = socket.socket()
            sock.connect((ip, port))
        except ConnectionRefusedError:
            error_message = "Tried connecting - server not available!"

        return sock

    def receiveAndCleanData(self, sock, expected_array_list_size):
        try:
            raw_data = sock.recv(4096)
            data_list = self.returnUsableServerData(raw_data, expected_array_list_size)
            if not data_list:
                return None

            return data_list

        except:
            return None

    def returnUsableServerData(self, raw_data, expected_array_list_size):
        data = raw_data.decode('utf-8')
        if "n" in data:
            data = data.replace("n", "")
        data_list = data.split(" ")
        try:
            data_list = list(map(int, data_list))

            while len(data_list) > expected_array_list_size:
                del data_list[len(data_list) - 2]
        except:
            return None

        return data_list


class AudioServerConnectionRunner:
    def __init__(self, service_settings, queue):
        self.service_settings = service_settings
        self.queue = queue

        self.audio_server_connection = AudioServerConnection(service_settings, queue)

    def run(self):
        driver_thread = threading.Thread(target=self.audio_server_connection.start)
        driver_thread.setDaemon(True)
        driver_thread.start()
