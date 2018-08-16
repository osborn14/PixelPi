from autobahn.asyncio.websocket import WebSocketClientProtocol

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
