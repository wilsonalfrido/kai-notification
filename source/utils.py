from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains



def configure_driver():
    service = Service(executable_path="driver\chromedriver-win64\chromedriver.exe")
    chrome_options = Options()

    chrome_options.add_experimental_option("detach",False)
    driver = webdriver.Chrome(service=service,options=chrome_options)

    return driver

def tap_middle_of_element(driver: webdriver.Remote, element, wait=500, num_of_taps=1):
    action = ActionChains(driver)
    # Get the location and size of the element
    element_location = element.location
    element_size = element.size
    
    # Calculate the middle point of the element
    middle_x = element_location['x'] + element_size['width'] / 2
    middle_y = element_location['y'] + element_size['height'] / 2
    element.click()
    # for _ in range(num_of_taps):
    #     action.move_to_element(element).click()

def find_element_and_tap(driver: webdriver.Remote, by, value, use_position=False, wait_time=5):
    wait = WebDriverWait(driver, wait_time)
    element = wait.until(EC.presence_of_element_located((by,value)))

    # if element.get_attribute("clickable") and not use_position:
    #     element.click()
    # else:
    tap_middle_of_element(driver, element,1)

def fill_book_data(book_data:dict):
 """
 book_data.keys = from,to,depart_date,
 """

 