from sqlalchemy import create_engine

class Connector():
    def __init__(self, host, id, passwd, db_name): 
        url = f"mysql+pymysql://{id}:{passwd}@{host}/{db_name}"
        self.engine = create_engine(url, echo=False, future=True)
        self.conn = self.engine.connect()

    def get_engine(self):
        return self.engine
    
    def get_connection(self):
        return self.conn
    