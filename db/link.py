from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
Base = declarative_base()

class Link(Base):
    __tablename__ = "link"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer)
    user_id = Column(Integer)
    link = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    