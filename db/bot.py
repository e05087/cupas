from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Float, String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
Base = declarative_base()

class Bot(Base):
    __tablename__ = "bot"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(Text)
    login_id = Column(Text)
    passwd = Column(Text)
    key = Column(Text)
    is_official = Column(Boolean, default=0)
    client = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    