from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from source.utils import retry

import pandas as pd

def get_ticket_data(driver: webdriver,book_data:dict):
    book_date = book_data["depart_date"]

    #1. Fill book data and submit
    fill_book_data(driver,book_data)

    #2. get all tickets data
    df_ticket_data = scrap_all_ticket(driver)
    df_ticket_data.to_csv(f"ticket_data_{book_date}.csv")


def fill_book_data(driver: webdriver,book_data:dict):
    """
    book_data.keys = origin,destination,depart_date : DD-MM-YYYY,
    """
    wait: WebDriverWait = WebDriverWait(driver, 10)

    #1. fill origin place
    fill_origin_place(driver,book_data)

    #2. fill destination place
    fill_destination_place(driver,book_data)

    #3 fill depart date
    fill_depart_date(driver,book_data)

    #4. submit
    wait.until(EC.presence_of_element_located((By.ID, 'submit'))).click()


##################################################################### UTILS #####################################################################

@retry(3, timeout=5, timewait=1)
def fill_origin_place(driver,book_data):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    origin_element = wait.until(EC.presence_of_element_located((By.ID, 'origination-flexdatalist')))
    origin_element.send_keys(book_data["origin"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="origination-flexdatalist-results"]/li[2]'))).click()

@retry(3, timeout=5, timewait=1)
def fill_destination_place(driver,book_data):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    destination_element = wait.until(EC.presence_of_element_located((By.ID, 'destination-flexdatalist')))
    destination_element.send_keys(book_data["destination"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="destination-flexdatalist-results"]/li[2]'))).click()

@retry(3, timeout=5, timewait=1)
def fill_depart_date(driver: webdriver,book_data):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    depart_date = book_data["depart_date"].split("-")

    dep_day = int(depart_date[0])
    dep_month = int(depart_date[1])
    dep_year = int(depart_date[2])
    #TODO debug if there are more than 1 available year
    
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="departure_dateh"]'))).click()
    month_min = int(wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]/option[1]'))).get_attribute("value"))

    if(month_min >= dep_month-1):
        month_index = (dep_month-1-month_min) + 1
        month_min = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="ui-datepicker-div"]/div/div/select[1]/option[{month_index}]'))).click()

    days_element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ui-state-default')))
    days_element[dep_day-1].click()

@retry(3, timeout=5, timewait=1)
def scrap_all_ticket(driver) -> pd.DataFrame:
    wait: WebDriverWait = WebDriverWait(driver, 10)
    num_ticket = len(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'data-wrapper'))))

    ticket_data = []

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

    return df_ticket_data
