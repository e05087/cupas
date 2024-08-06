from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
Base = declarative_base()

class Wiki(Base):
    __tablename__ = "wiki"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    content = Column(Text)
    img_link = Column(Text)
    url = Column(Text)
    created_dt = Column(DateTime(timezone=False))
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    