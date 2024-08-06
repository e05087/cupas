from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Double, String, Integer, DateTime, Text, Boolean
from sqlalchemy.sql import func
Base = declarative_base()

class QnaAnswer(Base):
    __tablename__ = "qna_answer"
    __table_args__ = {'mysql_engine':'InnoDB'}
    __mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    qna_id = Column(Integer)
    user_id = Column(Text)
    is_accepted = Column(Boolean, server_default=0)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())
    