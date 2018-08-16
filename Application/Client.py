import json, queue, threading, datetime, calendar, sys, os, signal, argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from Application.Settings import Settings

## Create our settings file as a global variable
#settings = Settings()
# os.environ['TZ'] = settings_file.time_zone
#client_settings = settings.getUniversalClientSettings()
#interface_list = settings.getInterfaces()


def signal_handler(signal, frame):
    for interface in interface_list:
        interface.displayDefaultLights()

    sys.exit(0)

# def opt_parse():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-c', action='store_true', help='clear the display on exit')
#     args = parser.parse_args()
#     if args.c:
#         signal.signal(signal.SIGINT, signal_handler)
#
#
# def prepareArrayforDisplay(array):
#     if settings_file.device_type == '50':
#         return array[0]
#     else:
#         return array
#
#
#
# def displayLights():
# #    display_mode_list.append(Mode([29, 29, 128]))
# #    display_mode_list.append(Mode([0, 0, 0]))
#     while True:
#         for d in display_mode_list:
#             if type(d) == Mode:
#                 DEVICE_RUNNER.displayLights(d.rgb_values)
#
#             elif type(d) == Timer:
#                 if d.activated:
#                     DEVICE_RUNNER.displayLights(d.rgb_values)
#                 else:
#                     ## Untested code that get the current time to compare it to the user's desired task activation time.
#                     ## If the current time matchs the activation time, the mode is activated
#                     current_datetime = datetime.datetime.now()
#                     current_hour = int(current_datetime.hour)
#                     current_minute = int(current_datetime.minute)
#                     current_day = str(current_datetime.day)
#                     current_date = datetime.date.today()
#                     day_of_the_week = calendar.day_name[current_date.weekday()]
#                     if day_of_the_week == d.day and current_hour == d.hour and current_minute == d.minute:
#                         d.activated = True
#
#                     # displayFromJsonArray(server_message['display colors'])
#
#             elif type(d) == Sparkle:
#                 DEVICE_RUNNER.displayLights(d.getCurrentRgbValues())
#
#             #DEVICE_RUNNER.displayLights(d.rgb_values)
# ##        time.sleep(0.05)
        
class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        ## Send server some basic details about the device upon connecting
##        device_name = settings_file.device_name
##        device_code = settings_file.device_code
##        device_type = settings_file.device_type
##        device_location = "temp"
##        self.sendMessage(json.dumps({'cmd' : 'REGISTER DEVICE', 'device_name':device_name ,'device code': device_code, 'device_type': device_type}).encode('utf8'))


    def onMessage(self, payload, isBinary):
        print("Message receicved!")
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            try:
                print(payload.decode('utf-8'))
                server_message = json.loads(payload.decode('utf-8'))
                print(type(server_message))
                ## Consider ids for removing orders
                ## Or, send a remove all command and send all again

                if server_message['cmd'] == 'DISPLAY':
                    ## Put the display mode into the proper category
                    if server_message['mode'] == 'simple':
                        for m in display_mode_list:
                            if type(m)  == Mode:
                                display_mode_list.remove(m)
                        display_mode_list.append(Mode(prepareArrayforDisplay(server_message['rgb array'])))
                    elif server_message['mode'] == 'timer':
                        display_mode_list.append(Timer(server_message['timer day'], server_message['timer hour'], server_message['timer minute'], prepareArrayforDisplay(server_message['rgb array'])))
                    display_queue.put(payload)
                    print("Text message received: {0}".format(payload.decode('utf8')))
            except:
                if int(payload.decode('utf-8')) % 100 == 0:
                    print(payload.decode('utf-8'))
                print("Server sent invalid json!")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        sys.exit()



# def displayLightsFromAudio():
#     # audio_server_connection = AudioServerConnection()
#
#     while True:
#         # audio_data = audio_server_connection.getAudioServerData()
#
#
#         for interface in interface_list:
#             # if audio_data.music_is_playing:
#             #     interface.displayAudioLights(audio_data)
#             # else:
#             interface.displayDefaultLights()


if __name__ == '__main__':
    
    # Process arguments
    # opt_parse()
    # display_mode_list = list()
        
    # display_queue = queue.Queue()
    # connection_to_audio_server_thread = threading.Thread(target=displayLightsFromAudio)
    # connection_to_audio_server_thread.setDaemon(True)
    # connection_to_audio_server_thread.start()

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        import trollius as asyncio

    factory = WebSocketClientFactory(u"ws://" + "127.0.0.1" + ":" + str(9000))
    factory.protocol = MyClientProtocol



    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, "127.0.0.1", 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()





