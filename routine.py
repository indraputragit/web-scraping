import logging
import os
import schedule
import sys
import time

path = os.getcwd()

logging.basicConfig(filename="{}/monitor.log".format(path),
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
 
def process():

    try:
        os.system("python3 {}/scrape_klikindomaret.py".format(path))
        logger.info("Success scrape klikindomaret")
    except Exception as Argument: 
        logging.exception("Error occurred while scrape klikindomaret") 

    # try:
    #     os.system("python3 {}/scrape_tokopedia.py".format(path))
    #     logger.info("Success scrape tokopedia")
    # except Exception as Argument: 
    #     logging.exception("Error occurred while scrape tokopedia")

    try:
        os.system("python3 {}/predict_price.py".format(path))
        logger.info("Success to process price recommendation")
    except Exception as Argument: 
        logging.exception("Error occurred while process price recommendation")

if __name__ == "__main__":
    # schedule.every(5).minutes.do(process)
    schedule.every().day.at("19:00").do(process)

    while True:
        schedule.run_pending()
        time.sleep(1)