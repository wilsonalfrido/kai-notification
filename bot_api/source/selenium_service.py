import requests
import logging
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)

def is_server_running(port) -> bool:
    """ Check if the Selenium server is running on the given port. """
    try:
        response = requests.get(f"http://127.0.0.1:{port}/wd/hub/status")
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def start_selenium_servers(port, max_retries: int = 10, delay: float = 2) -> bool:
    """ Start the Appium server on a specified port with retries. """

    logger.info(f"Initiating Selenium service on http://127.0.0.1:{port}/wd/hub")
    webdriver.Chrome(ChromeDriverManager(port=port).install())

    retry = 0
    while retry < max_retries:
        if is_server_running(port):
            logger.info(
                f"Selenium service on http://127.0.0.1:{port}/wd/hub is successfully initiated!")
            return True
        time.sleep(delay)
        retry += 1
        logger.info(
            f"Retrying to start Selenium service on http://127.0.0.1:{port}/wd/hub (Attempt {retry}/{max_retries})")

    logger.error(
        f"Failed to start Appium service on http://127.0.0.1:{port}/wd/hub after {max_retries} attempts.")
    return False