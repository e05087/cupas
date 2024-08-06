from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
Base = declarative_base()

class Qna(Base):
    __tablename__ = "qna"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Text)
    link = Column(Text)
    title = Column(Text)
    keyword = Column(Text)
    created_by_us = Column(Boolean, default=False)
    content_created_at = Column(DateTime(timezone=False))
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    