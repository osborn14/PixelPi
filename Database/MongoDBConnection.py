import pymongo


class MongoDBConnection:
    def __init__(self):
        self.pixel_pi_db_name = "PixelPiDB"

        self.db_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.pixel_pi_db = self.self.db_client[self.pixel_pi_db_name]

        all_mongo_db_list = self.db_client.list_database_names()
        if self.pixel_pi_db_name not in all_mongo_db_list:
            print("The database exists.")