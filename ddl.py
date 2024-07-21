from db.connector import Connector
from sqlalchemy.orm import sessionmaker
from settings import Settings
from db.content import Base as ContentBase
from db.post import Base as PostBase
from db.link import Base as LinkBase
from db.post_log import Base as PostLogBase

if __name__ == '__main__':
    setting = Settings()
    connector = Connector(setting.db_host, setting.db_id, setting.db_passwd, setting.db_name)
    engine = connector.get_engine()
    ContentBase.metadata.create_all(engine, checkfirst=True)
    PostBase.metadata.create_all(engine, checkfirst=True)
    LinkBase.metadata.create_all(engine, checkfirst=True)
    PostLogBase.metadata.create_all(engine, checkfirst=True)

    Session = sessionmaker(bind=engine)

    # Commit the changes and close the session
    session = Session()
    session.commit()
    session.close()