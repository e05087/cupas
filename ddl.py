from db.connector import Connector
from sqlalchemy.orm import sessionmaker
from settings import Settings
from db.content import Base as ContentBase
from db.post import Base as PostBase
from db.link import Base as LinkBase
from db.post_log import Base as PostLogBase
from db.wiki import Base as WikiBase
from db.info import Base as InfoBase
from db.info_log import Base as InfoLogBase
from db.neighbor import Base as NeighborBase
from db.qna import Base as QnaBase
from db.qna_answer import Base as QnaAnswerBase

if __name__ == '__main__':
    setting = Settings()
    connector = Connector(setting.db_host, setting.db_id, setting.db_passwd, setting.db_name)
    engine = connector.get_engine()
    ContentBase.metadata.create_all(engine, checkfirst=True)
    PostBase.metadata.create_all(engine, checkfirst=True)
    LinkBase.metadata.create_all(engine, checkfirst=True)
    PostLogBase.metadata.create_all(engine, checkfirst=True)
    WikiBase.metadata.create_all(engine, checkfirst=True)
    InfoBase.metadata.create_all(engine, checkfirst=True)
    InfoLogBase.metadata.create_all(engine, checkfirst=True)
    NeighborBase.metadata.create_all(engine, checkfirst=True)
    QnaBase.metadata.create_all(engine, checkfirst=True)
    QnaAnswerBase.metadata.create_all(engine, checkfirst=True)

    Session = sessionmaker(bind=engine)

    # Commit the changes and close the session
    session = Session()
    session.commit()
    session.close()