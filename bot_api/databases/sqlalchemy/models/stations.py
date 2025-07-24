from uuid import uuid4
from sqlalchemy import Boolean, Integer,Column, DateTime, ForeignKey, Uuid, Text,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData


metadata_obj = MetaData(schema="kai_notif")
Base = declarative_base(metadata=metadata_obj)

class Stations(Base):
    __tablename__ = "stations"

    code = Column(Text, primary_key=True, index=True)
    name = Column(Text,nullable=False)
    city = Column(Text,nullable=False)
    cityname = Column(Text,nullable=False)

