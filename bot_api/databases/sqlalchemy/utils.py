from databases.sqlalchemy.models.scheduler_tasks import SchedulerTasks
from databases.sqlalchemy.models.stations import Stations
from databases.sqlalchemy.database import Database
import uuid
from sqlalchemy import func

import pandas as pd

from databases.configs import DB_ENGINE

db_client = Database(DB_ENGINE=DB_ENGINE)

def insert_db_scheduler_tasks(chat_id:str,origin:str,destination:str,depart_date:str,depart_time:str,interval_scheduler:int,list_ticket_code:str):
    id = str(uuid.uuid4())
    new_task = SchedulerTasks(
        id = id,
        chat_id = chat_id,
        origin = origin,
        destination = destination,
        depart_date = depart_date,
        depart_time = depart_time,
        interval_scheduler =  interval_scheduler,
        list_ticket_code  = list_ticket_code 
    )

    db_client.insert(new_task)

    return id

def get_db_list_active_scheduler_user(chat_id:str) -> pd.DataFrame:
    user_filter = [
        SchedulerTasks.chat_id.in_([str(chat_id)]),
        SchedulerTasks.status.in_(["active"])
    ]

    df_list_scheduler = db_client.read(target=SchedulerTasks,filters=user_filter)

    return df_list_scheduler

def get_db_all_active_scheduler() -> pd.DataFrame:
    user_filter = [
        SchedulerTasks.status.in_(["active"])
    ]

    df_list_scheduler = db_client.read(target=SchedulerTasks,filters=user_filter)

    return df_list_scheduler

def get_db_scheduler_by_id(id:list) -> pd.DataFrame:
    scheduler = [
        SchedulerTasks.id.in_(id)
    ]

    df_list_scheduler = db_client.read(target=SchedulerTasks,filters=scheduler)

    return df_list_scheduler

def update_db_scheduler_status(id:str):
    db_client.update(
        target=SchedulerTasks,
        id=id,
        updates={"status": "non active","updated_at":func.now()},
    )

def get_db_list_stations():
    df_list_stations = db_client.read(target=Stations)

    return df_list_stations



    





