import time
from source.utils import configure_driver
from source.fill_book_data import fill_book_data

def main():
    book_data = {
        "origin": "sukabumi",
        "destination": "bogor",
        "depart_date" : "15-04-2024"
    }
    driver = configure_driver()
    driver.maximize_window()
    driver.get("https://booking.kai.id/")
    driver.refresh()
    driver.refresh()
    fill_book_data(driver,book_data)
    time.sleep(20)
    driver.refresh()
        

if __name__ == '__main__':
    main()