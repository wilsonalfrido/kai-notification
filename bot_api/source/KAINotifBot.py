from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import (
    Application,
)
from telegram import Update



class KaiNotifBot:
    def __init__(self,token) -> None:
        self.scheduler = BackgroundScheduler()
        self.application = Application.builder().token(token).build()

    def start_bot(self,list_handler): 
        for handler in list_handler:
            self.application.add_handler(handler)
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    