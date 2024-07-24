from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from source.get_ticket_data import get_ticket_data, get_ticket_data_str
from databases.sqlalchemy.utils import get_db_list_active_scheduler_user,get_db_all_active_scheduler,get_db_scheduler_by_id,update_db_scheduler_status
from apscheduler.schedulers.background import BackgroundScheduler

from source.logger import create_logger
logger = create_logger(__name__)

async def notif_scheduler_task(scheduler:BackgroundScheduler,id,token,chat_id,input_book_data,interval,stage,list_filter_ticket_code:list):
    bot = Bot(token=token)

    df_ticket_data = get_ticket_data(input_book_data,stage,list_filter_ticket_code)

    if(df_ticket_data is None):
        scheduler_str = get_scheduler_by_id_str(id=id)
        status,status_str= update_scheduler_status(id=id)
        ticket_data_str = status_str + "\n" + "**Expired Book Date**\n" + scheduler_str
        if(status == "success"):
            scheduler.remove_job(job_id=id)
    else:
        ticket_data_str = get_ticket_data_str(df_ticket_data,input_book_data,interval)

    if(ticket_data_str):
        await bot.send_message(chat_id=chat_id, text=ticket_data_str,parse_mode=ParseMode.MARKDOWN_V2)

def run_notif_scheduler_task(scheduler:BackgroundScheduler,id,token,chat_id,input_book_data,stage,list_filter_ticket_code,interval=None):

    asyncio.run(notif_scheduler_task(scheduler,id,token,chat_id,input_book_data,interval,stage,list_filter_ticket_code))

def get_list_notif_scheduler_str(chat_id) -> str:
    df_list_scheduler = get_db_list_active_scheduler_user(chat_id)
    df_list_scheduler_filt = df_list_scheduler[["origin","destination","depart_date","interval_scheduler"]].copy()
    df_list_scheduler_filt["interval_scheduler"] = df_list_scheduler_filt["interval_scheduler"].apply(lambda x: str(x) + " min") 
    df_list_scheduler_filt.rename(columns={"interval_scheduler":"interval"},inplace=True)

    dict_notif = get_dict_notif_scheduler(chat_id)
    list_notif = [dict_notif[id] for id in dict_notif.keys()]
    
    table_data = [list(df_list_scheduler_filt.columns)] + df_list_scheduler_filt.values.tolist()
    table_str = "`**List Active Scheduler**`" + "\n```{}\n{}```".format(
        "/".join(table_data[0]),
        "\n".join(list_notif)
    )
        

    return table_str

def get_dict_notif_scheduler(chat_id) -> str:
    df_list_scheduler = get_db_list_active_scheduler_user(chat_id)
    df_list_scheduler.sort_values(by="created_at",ascending=True,inplace=True)

    dict_notif = dict()
    for id in df_list_scheduler["id"].values:
        temp = df_list_scheduler[df_list_scheduler["id"] == id]
        str_notif_data = temp["origin"].values[0] + "-" + temp["destination"].values[0] + "/" + temp["depart_date"].values[0] + "/" + str(temp["interval_scheduler"].values[0]) + " min"
        dict_notif[id] = str_notif_data
    
    return dict_notif

def run_all_active_scheduler(token,scheduler:BackgroundScheduler):

    df_all_active_scheduler = get_db_all_active_scheduler()

    logger.info(f'Initialize running {df_all_active_scheduler.shape[0]} KAI Notification scheduler ...')

    for id in df_all_active_scheduler["id"].values:
        temp_df = df_all_active_scheduler[df_all_active_scheduler["id"] == id].copy()
        input_book_data = {
            "origin": temp_df["origin"].values[0],
            "destination": temp_df["destination"].values[0],
            "depart_date" : temp_df["depart_date"].values[0],  
        }
        list_filter_ticket_code = (temp_df.loc[0,"list_ticket_code"]).split(",")
        scheduler.add_job(func=run_notif_scheduler_task,args=(scheduler,id,token,temp_df["chat_id"].values[0],input_book_data,"dev",list_filter_ticket_code,temp_df["interval_scheduler"].values[0]),trigger="interval",minutes=int(temp_df["interval_scheduler"].values[0]),id=id)

def get_scheduler_by_id_str(id) -> str:

    df_scheduler = get_db_scheduler_by_id([str(id)])
    
    str_scheduler = '\n```{}\n{}\n{}\n{}\n{}\n```'.format(
        id,
        "Origin : " + df_scheduler["origin"].values[0],
        "Destination : " + df_scheduler["destination"].values[0],
        "Depart Date : " + df_scheduler["depart_date"].values[0],
        "Interval : " + str(df_scheduler["interval_scheduler"].values[0]) + " min"
    )

    return str_scheduler

def update_scheduler_status(id):
    
    try:
        update_db_scheduler_status(id)
        
        status_str = f'Scheduler with Id : `{id}` successfully deleted'
        logger.info(f'Scheduler with Id : {id} successfully deleted')
        status = "success"
    except Exception as e:
        logger.error(f'Failed to delete scheduler with id : {id} -> {e}')
        status_str = f'Failed to delete scheduler with id : `{id}`'
        status = "failed"

    return status,status_str


