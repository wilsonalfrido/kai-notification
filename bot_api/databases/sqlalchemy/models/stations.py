from databases.sqlalchemy.models import Base
from uuid import uuid4
from sqlalchemy import Boolean, Integer,Column, DateTime, ForeignKey, Uuid, Text,func


class Stations(Base):
    __tablename__ = "stations"

    code = Column(Text, primary_key=True, index=True)
    name = Column(Text,nullable=False)
    city = Column(Text,nullable=False)
    cityname = Column(Text,nullable=False)

