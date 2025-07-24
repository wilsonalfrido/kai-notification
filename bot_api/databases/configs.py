import os
from sqlalchemy import URL, create_engine
from dotenv import load_dotenv
import logging


load_dotenv(".env")

STAGE = os.getenv("STAGE")

logger = logging.getLogger(__name__)
logger.info(f'Configuring DB for {STAGE}')

if(STAGE == "PROD"):
    PG_HOST = os.getenv("PG_HOST_PROD")
    PG_PORT = os.getenv("PG_PORT_PROD")
else:
    PG_HOST = os.getenv("PG_HOST_DEV")
    PG_PORT = os.getenv("PG_PORT_DEV")
PG_USER = os.getenv("PG_USER")
PG_DRIVER = os.getenv("PG_DRIVER")
PG_SCHEMA = os.getenv("PG_SCHEMA")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")

db_url = URL.create(
    drivername=PG_DRIVER,
    username=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
)

DB_ENGINE = create_engine(
    url=db_url
)