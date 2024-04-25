import time
import os
from source.utils import configure_driver
from source.get_ticket_data import get_ticket_data

from source.selenium_service import start_selenium_servers

from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
)

from source.bot_handler import KaiNotifBot

from apscheduler.schedulers.background import BackgroundScheduler

from tqdm import tqdm
from queue import Queue
import threading

if '.env' in os.listdir():
    load_dotenv('.env')
TOKEN = os.getenv("TOKEN"," ")

def main():

    kai_notif_bot = KaiNotifBot(TOKEN)
    kai_notif_bot.start_bot()

if __name__ == '__main__':
    main()