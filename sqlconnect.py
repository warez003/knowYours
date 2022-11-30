
import sqlite3

class Connect:
    
    def __init__(self, str_connect):
        self.__str_connect = str_connect
    
    @property
    def str_connect(self):
        return self.__str_connect
    
    def query(self, str_query):
        con = sqlite3.connect(self.str_connect)
        cur = con.cursor()
        cur.execute(str_query)
        con.commit()
        return cur.fetchall()