import pymysql

class DatabaseConnection():
    def __init__(self):
        try:
            self.db = pymysql.connect("localhost", "root", "root", "PixelPi")
            self.cursor = self.db.cursor()

        except:
            self.db = pymysql.connect("localhost", "root", "root")
            self.cursor = self.db.cursor()

            self.cursor.execute("CREATE DATABASE PixelPi")
            self.cursor.execute("USE PixelPi;")
            self.cursor.execute("""CREATE TABLE Tasks(
                id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                device_name VARCHAR(4) NOT NULL,
                command TEXT NOT NULL);""")

        self.db.commit()

    def addTask(self, device_name, payload):
        return_dictionary = {'task id': 'n/a'}
        try:
            sql = "INSERT INTO Tasks(device_name, command)\
               VALUES ('%s', '%s')" % \
                  (device_name, payload)

            self.cursor.execute(sql)
            self.db.commit()

            self.cursor.excute('SELECT LAST_INSERT_ID()')
            return_dictionary['task id'] = self.cursor.fetchone()

        except:
            print("An unexpected error occurred")

        return return_dictionary

    def viewTasks(self, device_name):
        try:
            sql = "Select id, device_name, command FROM Tasks\
               WHERE device_name = '%s'" % \
                  (device_name)

            self.cursor.execute(sql)
            sql_results = self.cursor.fetchall()
            sql_results_dict = {'tasks': []}

            for row in sql_results:
                temp_dict = {'json': row[2]}
                sql_results_dict['tasks'].append(temp_dict)

            return sql_results_dict

        except:
            print("An unexpected error occurred")
            return None

    def removeTask(self, id):
        try:
            sql = "DELETE FROM Tasks\
               WHERE id = '%s'" % \
                  (id)

            self.cursor.execute(sql)
            self.db.commit()
            return True

        except:
            return False