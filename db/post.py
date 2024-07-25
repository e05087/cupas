from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Double, String, Integer, DateTime, Text
from sqlalchemy.sql import func
Base = declarative_base()

class Post(Base):
    __tablename__ = "post"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer)
    target = Column(Text)
    title = Column(Text)
    body = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    