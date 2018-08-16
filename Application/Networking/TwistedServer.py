import json

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor

#from Application.Database.ClientTaskDatabase import ClientTaskDatabase

#database = ClientTaskDatabase()
connected_device_list = list()

class Device():
    def __init__(self, category, name, client, description):
        self.category = category;
        self.name = name
        self.client = client
        self.description = description

class BroadcastServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))
        connected_device_list.append(Device('AD', 'ad01', self, 'Admin'))

    def onMessage(self, payload, isBinary):
        print("Message received")

        if not isBinary:
            msg = json.loads(payload.decode('utf8'))
            print(msg)

            if msg['cmd'] == 'AUTHENTICATE':
                print('un' + msg['username'])
                print('pw' + msg['password'])
                login_status = database.authenticateUser(msg['username'], msg['password'])
                print(str(login_status))
                self.sendMessage(json.dumps({'cmd': 'AUTHENTICATE', 'status': str(login_status)}).encode('utf8'))

            if msg['cmd'] == 'REGISTER DEVICE':
                if str(msg['device code'])[:2] == 'AD':
                    print("Android device connected!")
                    print(msg['device code'])
                    connected_device_list.append(Device('AD', msg['device code'], self, 'Admin'))
                else:
                    connected_device_list.append(Device('NP', msg['device code'], self, 'Neopixel client'))

                    device_tasks = database.viewTasks(msg['device code'])
                    for t in device_tasks['tasks']:
                        print(t['json'])
                        self.sendMessage(t['json'].encode('utf8'))


            ##            elif msg['cmd'] == 'CLEAR':
            ##                removeTask(msg['id'])
            ##                sendJsonToSingleClient(msg)

            elif msg['cmd'] == 'DISPLAY':
                if 'task id' in msg:
                    database.addTask('NP01', json.dumps(payload.decode('utf8')))
                for cd in connected_device_list:
                    if 'NP01' == cd.name:
                        cd.client.sendMessage(payload)
                        print("Message sent! - NP")

            elif msg['cmd'] == 'VIEW AVAILABLE CLIENTS':
                all_devices_dict = {'cmd': 'VIEW AVAILABLE CLIENTS', 'devices': []}
                for cd in connected_device_list:
                    if cd.category != 'AD':
                        print("Name added!" + cd.name)

                        device_dict = {'device code': cd.name}
                        dict(device_dict, **database.viewTasks(cd.name))
                        all_devices_dict['devices'].append(device_dict)

                self.sendMessage(json.dumps(all_devices_dict).encode('utf8'))

        # self.factory.broadcast(payload.decode("utf-8"))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    @classmethod
    def broadcast_audio_data(cls, payload):
        for cd in connected_device_list:
            reactor.callFromThread(cls.sendMessage, cd.client, payload)


class BroadcastServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        self.tick()

    def tick(self):
        self.tickcount += 1

    ##        self.broadcast("tick %d from server" % self.tickcount)
    ##        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            print(c)
            ##            if msg['send to'] == c.
            c.sendMessage(msg)
            print("message sent to {}".format(c.peer))


class BroadcastPreparedServerFactory(BroadcastServerFactory):
    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))