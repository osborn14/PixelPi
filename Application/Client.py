import json, queue, threading, datetime, calendar, sys, os, signal, argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Application.Networking.TwistedClient import MyClientProtocol
from Application.Settings import Settings

from autobahn.asyncio.websocket import WebSocketClientFactory

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
        


#TODO: If there is no data received from server after 15 seconds, resume default display.
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





