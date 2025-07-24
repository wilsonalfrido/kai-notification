from uuid import uuid4
from sqlalchemy import Boolean, Integer,Column, DateTime, ForeignKey, Uuid, Text,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

metadata_obj = MetaData(schema="kai_notif")
Base = declarative_base(metadata=metadata_obj)


class SchedulerTasks(Base):
    __tablename__ = "scheduler_tasks"

    id = Column(Text, primary_key=True, index=True, default=uuid4)
    chat_id = Column(Text,nullable=False)
    list_ticket_code = Column(Text,nullable=False)
    origin = Column(Text,default=False)
    destination = Column(Text,default=False)
    depart_date = Column(Text,default=False)
    depart_time = Column(Text,default=False)
    interval_scheduler =  Column(Integer,default=False)
    status = Column(Text,default = "active")
    created_at = Column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
