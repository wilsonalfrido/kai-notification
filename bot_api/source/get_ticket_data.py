import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from urllib.parse import urlencode
import logging

from databases.sqlalchemy.utils import get_db_list_stations
from source.utils import retry
logger = logging.getLogger(__name__)

# @retry(2, timeout=5, timewait=1)
def get_ticket_data(book_data:dict,stage,list_filter_ticket_code) -> pd.DataFrame:
    book_date = datetime.strptime(book_data["depart_date"], "%d-%m-%Y").date()
    now_date = datetime.today().date()
    logger.info(f'Check in func list_filterticket : {list_filter_ticket_code}, type : {type(list_filter_ticket_code)}')
    if(now_date <= book_date):
        content = get_api_booking_content(book_data)
        df_ticket_data = parse_request_api(content,list_filter_ticket_code)
        return df_ticket_data
    else:
        logger.info("Expired book date")
        return None

def get_ticket_data_str(df_ticket_data,book_data:dict,interval=None) -> str:
    if(isinstance(df_ticket_data,pd.DataFrame)):
        if(df_ticket_data.shape[0] > 0):
            df_ticket_data = df_ticket_data[df_ticket_data["is_avail"] == True].copy()
            df_ticket_data["seat"] = df_ticket_data["is_avail"].apply(lambda x: ("available" if x == True else "not avail"))
            # df_ticket_data["is_avail"] = df_ticket_data["is_avail"].astype(str)
            df_ticket_data = df_ticket_data[["class","depart_time","seat"]].copy()
            # df_ticket_data.rename(columns={"depart_time":"depart_time"}, inplace=True)
            df_ticket_data["class"] = df_ticket_data["class"].apply(lambda x: x.replace("(","\(").replace(")","\)"))
            table_data = [list(df_ticket_data.columns)] + df_ticket_data.values.tolist()
            table_str = '`**KAI Ticket Scheduler**`\n'+'```{}-{}/{}\nInterval : {}```'.format(
                book_data["origin"],
                book_data["destination"],
                book_data["depart_date"],
                ((str(interval) + "min") if interval else "\-")
            ) + "\n```{}\n{}```".format(
                "-".join(table_data[0]), 
                "\n".join(["-".join(row) for row in (table_data[1:])])
            ) 
        elif(interval and df_ticket_data.shape[0] == 0):
            table_str = None
        else:
            table_str = '`**KAI Ticket Scheduler**`\n' + '**Ticket Doesn\'t Exist\!**'
            # table_str = None
    else:
        table_str = '`**KAI Ticket Scheduler**`\n' + '**Expired Book Date**'


    return table_str

@retry(2, timeout=5, timewait=1)
def get_list_ticket(book_data:dict) -> dict:
    ticket_dict = {}
    content = get_api_booking_content(book_data)
    if(content):
        soup = BeautifulSoup(content, 'html.parser')
        data_wrapper = soup.find_all('div', class_='data-wrapper')

        for data in data_wrapper:
            ticket_sub_code= data.find("input",{"name":"nokereta"})["value"]
            ticket_class = data.find("div", {"class": "{kelas kereta}"}).text

            ticket_code = f'{ticket_sub_code}_{ticket_class}'
            depart_time = data.find("div", {"class": ["times","time-start"]}).text
            ticket_dict[ticket_code] = f'{ticket_class} {depart_time}'
    
    return ticket_dict


def get_api_booking_content(book_data) -> str:
    def form_booking_url(origination, flexdatalist_origination, destination, flexdatalist_destination, tanggal):
        """Form the booking URL with the given parameters."""
        base_url = "https://booking.kai.id/"
        params = {
            "origination": origination,
            "flexdatalist-origination": flexdatalist_origination,
            "destination": destination,
            "flexdatalist-destination": flexdatalist_destination,
            "tanggal": tanggal,
            "adult": 1,
            "infant": 0,
            "submit": "Cari & Pesan Tiket"
        }
        return base_url + "?" + urlencode(params)

    def fetch_url_content(url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()  # This will raise an HTTPError if the status is 4xx, 5xx

    content = None
    origin = str(book_data["origin"]).upper()
    destination = str(book_data["destination"]).upper()
    depart_date = book_data["depart_date"]

    station_dict = get_station_code_dict()

    if(origin in station_dict.keys()):
        origin_code = station_dict[origin]
    else:
        raise ValueError(f'Origin code of {origin} is not exist')
    
    if(destination in station_dict.keys()):
        destination_code = station_dict[destination]
    else:
        raise ValueError(f'Destination code of {origin} is not exist')
    
    url = form_booking_url(origination=origin_code,
                           flexdatalist_origination=origin,
                           destination=destination_code,
                           flexdatalist_destination=destination,
                           tanggal=depart_date)
    
    try:
        content = fetch_url_content(url)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    
    return content

def parse_request_api(content,list_filter_ticket_code):
    ticket_data = []
    if(content):
        soup = BeautifulSoup(content, 'html.parser')
        data_wrapper = soup.find_all('div', class_='data-wrapper')

        for data in data_wrapper:
            ticket_class = data.find("div", {"class": "{kelas kereta}"}).text
            depart_time = data.find("div", {"class": ["times","time-start"]}).text
            is_avail = data.find("small", {"class": ["form-text","sisa-kursi"]}).text

            ticket_sub_code= data.find("input",{"name":"nokereta"})["value"]
            ticket_class = data.find("div", {"class": "{kelas kereta}"}).text

            ticket_code = f'{ticket_sub_code}_{ticket_class}'

            if((is_avail.lower() != "habis")and(ticket_code in list_filter_ticket_code)):
                temp = {
                    "class" : ticket_class,
                    "depart_time" : depart_time,
                    "is_avail" : True                    
                }
                ticket_data.append(temp)
    
    df_ticket_data = pd.DataFrame(ticket_data)

    return df_ticket_data

def get_station_code_dict() -> dict:
    df_list_station = get_db_list_stations()
    station_code_dict = df_list_station[["name","code"]].set_index("name")["code"].to_dict()    

    return station_code_dict

