from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from source.utils import retry
from source.utils import configure_driver
from datetime import datetime
import time

import pandas as pd

from source.logger import create_logger
logger = create_logger(__name__)
##################################################################### MAIN #####################################################################

def get_ticket_data(book_data:dict,stage) -> pd.DataFrame:

    driver = configure_driver(stage)
    # driver.get("https://booking.kai.id/")
    # driver.refresh()
    # driver.refresh()


    book_date = datetime.strptime(book_data["depart_date"], "%d-%m-%Y").date()
    now_date = datetime.today().date()
    action = ActionChains(driver)

    
    if(now_date <= book_date):
        #1. Fill book data and submit
        fill_book_data(driver,book_data,action)
        time.sleep(5)

        #2. get all tickets data
        df_ticket_data = scrap_all_ticket(driver)
        driver.quit()
        
        return df_ticket_data
    else:
        return None

def get_ticket_data_str(df_ticket_data: pd.DataFrame,book_data:dict,interval=None) -> str:

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

##################################################################### UTILS #####################################################################

@retry(3, timeout=5, timewait=1)
def fill_book_data(driver: webdriver,book_data:dict,action:ActionChains):
    """
    book_data.keys = origin,destination,depart_date : DD-MM-YYYY,
    """
    driver.get("https://booking.kai.id/")
    driver.refresh()
    driver.refresh()
    wait: WebDriverWait = WebDriverWait(driver, 10)

    #1. fill origin place
    logger.info("Filling origin place ...")
    fill_origin_place(driver,book_data)

    #2. fill destination place
    logger.info('Filling destination place ...')
    fill_destination_place(driver,book_data)

    #3 fill depart date
    logger.info('Filling depart date ...')
    fill_depart_date(driver,book_data,action)

    #4. submit
    logger.info('Submitting book data ...')
    try:
        submit_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="submit"]')))
        # action.move_to_element(wait.until(EC.element_to_be_clickable(submit_element))).click().perform()
        submit_element.click()
    except:
        submit_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn sample btn-sample btn-search-booking')))
        submit_element.click()


# @retry(2, timeout=5, timewait=1)
def fill_origin_place(driver,book_data):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    origin_element = wait.until(EC.presence_of_element_located((By.ID, 'origination-flexdatalist')))
    origin_element.send_keys(book_data["origin"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="origination-flexdatalist-results"]/li[2]'))).click()

# @retry(2, timeout=5, timewait=1)
def fill_destination_place(driver,book_data):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    destination_element = wait.until(EC.presence_of_element_located((By.ID, 'destination-flexdatalist')))
    destination_element.send_keys(book_data["destination"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="destination-flexdatalist-results"]/li[2]'))).click()

# @retry(2, timeout=5, timewait=1)
def fill_depart_date(driver: webdriver,book_data,action:ActionChains):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    depart_date = book_data["depart_date"].split("-")

    dep_day = int(depart_date[0])
    dep_month = int(depart_date[1])
    dep_year = int(depart_date[2])
    #TODO debug if there are more than 1 available year
    
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="departure_dateh"]'))).click()
    month_min = int(wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]/option[1]'))).get_attribute("value"))

    logger.info(f'Month min : {month_min}')
    # driver.save_screenshot("./screenshot_2.png")

    month_click = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-datepicker-month')))
    action.move_to_element(wait.until(EC.element_to_be_clickable(month_click)))
    action.click().perform()

    month_index = (dep_month-month_min)
    month_min = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="ui-datepicker-div"]/div/div/select[1]/option[{month_index}]'))).click()

    try:
        days_element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ui-state-default')))
        days_element[dep_day-1].click()
    except:
        days_element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ui-state-default')))
        action.move_to_element(days_element[dep_day-1])
        action.click()
        action.perform()

@retry(2, timeout=5, timewait=1)
def scrap_all_ticket(driver:webdriver) -> pd.DataFrame:
    driver.save_screenshot("./screenshot.png")
    wait: WebDriverWait = WebDriverWait(driver, 15)
    try:
        try:
            num_ticket = len(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'data-wrapper'))))
        except:
            num_ticket = len(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'data-block list-kereta'))))
    except:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'notice-wrapper')))
        num_ticket = 0

    ticket_data = []

    # logger.info(f'Found {num_ticket} data ...')

    for i in range(0,num_ticket):
        ticket_class = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="data{i}"]/a/div/div[1]/div/div[2]'))).text
        depart_time = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="data{i}"]/a/div/div[2]/div/div/div[1]/div[2]'))).text
        availibility_status = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="data{i}"]/a/div/div[3]/div/small'))).text
        is_avail = (False if availibility_status == "Habis" else True)

        temp = {
            "class" : ticket_class,
            "depart_time" : depart_time,
            "is_avail" : is_avail
        }

        ticket_data.append(temp)

    df_ticket_data = pd.DataFrame(ticket_data)
    df_ticket_data = df_ticket_data[df_ticket_data["is_avail"] == True].copy()
    logger.info(f'Result : {df_ticket_data}')
    logger.info(f'Found {df_ticket_data.shape[0]} data ...')

    return df_ticket_data
