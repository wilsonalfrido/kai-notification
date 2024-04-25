from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains

import decorator
import time
import logging

logger = logging.getLogger(__name__)

def configure_driver():
    service = Service(executable_path="driver\chromedriver-win64\chromedriver.exe")
    chrome_options = Options()

    chrome_options.add_experimental_option("detach",False)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-webusb")

    prefs = {
        "profile.default_content_setting_values.webusb": 1  # 1 to disable, 2 to enable
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Step 3: Add preferences to Chrome options
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.maximize_window()

    return driver

def retry(howmany, **kwargs):
    timewait=kwargs.get('timewait', 1.0) # seconds
    timeout = kwargs.get('timeout', 0.0) # seconds
    raise_error = kwargs.get('raise_error', True)
    # exception_message=kwargs.get('exception_message', "ERROR")
    # success_message=kwargs.get('exception_message', "SUCCESS")
    time.sleep(timewait)
    @decorator.decorator
    def tryIt(func, *fargs, **fkwargs):
        for trial in range(howmany):
            try:
                logger.info(f"Execute function {func.__name__} at {trial} trial") 
                return func(*fargs, **fkwargs)
            except Exception as e:
                error_msg = f'Error in {func.__name__} function at {trial+1} trial : {e}'
                logger.error(f'{error_msg}')
                # logger.error(e)
                # on every exception, write down where does the exception and how many tries attempted
                if timeout is not None: time.sleep(timeout)
            # if the last attempt failed, raise exception
        if raise_error:
            raise Exception(f'{error_msg}')
        else:
            logger.error(f'{error_msg}')
            
    return tryIt

def fill_book_data(book_data:dict):
 """
 book_data.keys = from,to,depart_date,
 """

 