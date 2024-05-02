
import os

from dotenv import load_dotenv

from source.bot_handler import KaiNotifBot

from source.logger import create_logger
logger = create_logger(__name__)

if '.env' in os.listdir():
    load_dotenv('.env')
    
TOKEN = os.getenv("TOKEN"," ")
STAGE=os.getenv('STAGE','DEV')

def main():

    logger.info(f"{STAGE} service started")
    kai_notif_bot = KaiNotifBot(TOKEN,STAGE)
    kai_notif_bot.start_bot()

if __name__ == '__main__':
    main()