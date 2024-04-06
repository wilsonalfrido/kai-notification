from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from source.utils import find_element_and_tap

def fill_book_data(driver: webdriver,book_data:dict):
    """
    book_data.keys = origin,destination,depart_date : DD-MM-YYYY,
    """
    wait: WebDriverWait = WebDriverWait(driver, 10)
    

    #1. fill origin place
    origin_element = wait.until(EC.presence_of_element_located((By.ID, 'origination-flexdatalist')))
    origin_element.send_keys(book_data["origin"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="origination-flexdatalist-results"]/li[2]'))).click()
    

    #2. fill destination place
    destination_element = wait.until(EC.presence_of_element_located((By.ID, 'destination-flexdatalist')))
    destination_element.send_keys(book_data["destination"])
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="destination-flexdatalist-results"]/li[2]'))).click()

    #3 fill depart date
    

    fill_depart_month(driver,depart_date=book_data["depart_date"])

    wait.until(EC.presence_of_element_located((By.ID, 'submit'))).click()

# //*[@id="data0"]/a
# //*[@id="data0"]/a

    # #3.1 fill depart month




    
    # //*[@id="ui-datepicker-div"]/div/div/select[1]/option[1]

    # //*[@id="ui-datepicker-div"]/div/div/select[1]/option[3]

def fill_depart_month(driver: webdriver,depart_date):
    wait: WebDriverWait = WebDriverWait(driver, 10)
    depart_date = depart_date.split("-")

    dep_day = int(depart_date[0])
    dep_month = int(depart_date[1])
    dep_year = int(depart_date[2])
    
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="departure_dateh"]'))).click()
    month_min = int(wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]/option[1]'))).get_attribute("value"))

    if(month_min >= dep_month-1):
        month_index = (dep_month-1-month_min) + 1
        month_min = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="ui-datepicker-div"]/div/div/select[1]/option[{month_index}]'))).click()

    t = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ui-state-default')))
    t[dep_day-1].click()
    # print(f'len day {len(t)}')
    # for i in t:
    #     print(i.text)






