from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DtUser(Base):
    __tablename__ = "dt_user"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    face_img = Column(String)

