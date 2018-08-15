import sys, json, threading, time #, pymysql

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

class Device():
    def __init__(self, category, name, client, description):
        self.category = category;
        self.name = name
        self.client = client
        self.description = description

def addTask(device_name, payload):
    return_dictionary = {'task id': 'n/a'}
    try:
        sql = "INSERT INTO Tasks(device_name, command)\
           VALUES ('%s', '%s')" % \
           (device_name, payload)
           
        cursor.execute(sql)
        db.commit()

        cursor.excute('SELECT LAST_INSERT_ID()')
        return_dictionary['task id'] = cursor.fetchone()
        
    except:
        print("An unexpected error occurred")

    return return_dictionary

def viewTasks(device_name):
    try:
        sql = "Select id, device_name, command FROM Tasks\
           WHERE device_name = '%s'" % \
           (device_name)
           
        cursor.execute(sql)
        sql_results = cursor.fetchall()
        sql_results_dict = {'tasks': []}

        for row in sql_results:
            temp_dict = {'json': row[2]}
            sql_results_dict['tasks'].append(temp_dict)
        
        return sql_results_dict
        
    except:
        print("An unexpected error occurred")
        return None
    
def removeTask(id):
    try:
        sql = "DELETE FROM Tasks\
           WHERE id = '%s'" % \
           (id)
           
        cursor.execute(sql)
        db.commit()
        return True
        
    except:
        return False

def sendJsonToSingleClient(json):
    for cd in connected_device_list:
        if 'NP' == cd.category:
            print("Message sent! - NP")
            cd.client.sendMessage(payload)
        
class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onMessage(self, payload, isBinary):
        print("Message received")

        if not isBinary:
            msg = json.loads(payload.decode('utf8'))
            print(msg)

            if msg['cmd'] == 'AUTHENTICATE':
                print('un' + msg['username'])
                print('pw' + msg['password'])
                login_status = authenticateUser(msg['username'],  msg['password'])
                print( str(login_status))
                self.sendMessage(json.dumps({'cmd': 'AUTHENTICATE',  'status': str(login_status)}).encode('utf8'))

            if msg['cmd'] == 'REGISTER DEVICE':
                if str(msg['device code'])[:2] == 'AD':
                    print("Android device connected!")
                    print(msg['device code'])
                    connected_device_list.append(Device('AD',  msg['device code'], self, 'Admin'))
                else:
                    connected_device_list.append(Device('NP',  msg['device code'], self, 'Neopixel client'))

                    device_tasks = viewTasks(msg['device code'])
                    for t in device_tasks['tasks']:
                        print(t['json'])
                        self.sendMessage(t['json'].encode('utf8'))
                    
                    
##            elif msg['cmd'] == 'CLEAR':
##                removeTask(msg['id'])
##                sendJsonToSingleClient(msg)
                
                
            elif msg['cmd'] == 'DISPLAY':
                if 'task id' in msg:
                    addTask('NP01', json.dumps(payload.decode('utf8')))
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
                        dict(device_dict, **viewTasks(cd.name))
                        all_devices_dict['devices'].append(device_dict)
                        
                self.sendMessage(json.dumps(all_devices_dict).encode('utf8'))
                
        #self.factory.broadcast(payload.decode("utf-8"))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


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

def broadcastRepeatedly():
    i = 0
    while(True):
        msg = "Message: " + str(i)
        for cd in connected_device_list:
            cd.client.sendMessage()

        i += 1
        time.sleep(.01)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False
        
#     try:
#         db = pymysql.connect("localhost","root","root","PixelPi" )
#         cursor = db.cursor()
#
#     except:
#         db = pymysql.connect("localhost", "root", "root" )
#         cursor = db.cursor()
#
#         cursor.execute("CREATE DATABASE PixelPi")
#         cursor.execute("USE PixelPi;")
#         cursor.execute("""CREATE TABLE Tasks(
# id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
# device_name VARCHAR(4) NOT NULL,
# command TEXT NOT NULL);""")
#
#         db.commit()
        

    connected_device_list = list()
        
    ServerFactory = BroadcastServerFactory
    factory = ServerFactory("ws://127.0.0.1:9000")

    factory.protocol = BroadcastServerProtocol
    listenWS(factory)

    webdir = File(".")
    web = Site(webdir)
    print("Starting...")

    connection_to_audio_server_thread = threading.Thread(target=broadcastRepeatedly)
    connection_to_audio_server_thread.setDaemon(True)
    connection_to_audio_server_thread.start()

    reactor.run()
