import sys, json, threading, time #, pymysql

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Application.Settings import Settings
from Application.Networking.ServerConnection import AudioServerConnection
from Application.Common.AudioData import AudioData
import Application.Common.NetworkCommands as NETWORK

from Application.Networking.TwistedServer import BroadcastServerProtocol, BroadcastServerFactory


settings = Settings()
server_settings = settings.getServerSettings()

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



def broadcastAudioData():
    audio_server_connection = AudioServerConnection(server_settings)
    while(True):
        audio_data = audio_server_connection.getAudioServerData()
        if audio_data.music_is_playing:
            for cd in connected_device_list:
                msg = dict()
                msg[NETWORK.CMD] = NETWORK.DISPLAY
                msg[NETWORK.MODE] = NETWORK.AUDIO
                msg[NETWORK.AUDIO_DATA] = audio_data.getAudioJSON()

                cd.client.sendMessage(json.dumps(msg).encode('utf8'))

        time.sleep(.05)

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

    connection_to_audio_server_thread = threading.Thread(target=broadcastAudioData)
    connection_to_audio_server_thread.setDaemon(True)
    connection_to_audio_server_thread.start()

    reactor.run()
