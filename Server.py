

class Server():
    def __init__(self, settings):
        self.settings = settings

        ServerFactory = BroadcastServerFactory
        self.twisted_factory = ServerFactory("ws://127.0.0.1:9000")
        self.twisted_factory.protocol = BroadcastServerProtocol

    def run(self):
        connection_to_audio_server_thread = threading.Thread(target=self.broadcastAudioData)
        connection_to_audio_server_thread.setDaemon(True)
        connection_to_audio_server_thread.start()

        listenWS(self.twisted_factory)

        webdir = File(".")
        web = Site(webdir)
        print("Starting...")

        reactor.run()

    def broadcastAudioData(self):
        audio_server_connection = AudioServerConnection(self.settings)
        while (True):
            audio_data = audio_server_connection.getAudioServerData()
            if audio_data and audio_data.music_is_playing:
                msg = dict()
                msg[NETWORK.COMMAND] = NETWORK.DISPLAY
                msg[NETWORK.MODE] = NETWORK.AUDIO
                msg[NETWORK.AUDIO_DATA] = audio_data.getAudioJSON()

                # print("Should be printing...")

                factory.protocol.broadcast_audio_data(json.dumps(msg, ensure_ascii=False).encode('utf8'))

            time.sleep(.05)