from app.backend.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func



class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    title = Column(String)
    description = Column(String)
    status = Column(String)
    create_date = Column(DateTime(timezone=True), server_default=func.now())