import argparse
import os
import csv
import requests
import schedule
import time
from datetime import datetime


arg_parser = argparse.ArgumentParser(description='Scraps MMTP GOLD price')
arg_parser.add_argument(
    '-m', '--minutes', type=int, help='time interval between each scrap in minutes (default 30)', default=30, required=False)

args = arg_parser.parse_args()

SCRAP_URL = 'https://paytm.com/papi/v2/gold/product-portfolio?channel=WEB&version=2&child_site_id=1&site_id=1'
FILE_NAME = 'MMTC_GOLD_PRICE.csv'
TIME_INTERVAL = args.minutes


def get_price():
    """Returns price per gram and selling price per gram"""

    response = requests.get(SCRAP_URL)

    if response.ok:
        data = response.json()
        price_per_gm = data['portfolio']['product_level'][0]['price_per_gm']
        selling_price_per_gm = data['portfolio']['product_level'][0]['sell_price_per_gm']

        print(
            f'Price: {price_per_gm}, Selling Price: {selling_price_per_gm} [{datetime.now()}]')

        return price_per_gm, selling_price_per_gm

    raise Exception(f"Unable to fetch, time: {datetime.now()} ")


def create_csv(filename=FILE_NAME):
    """Creates initial csv file"""

    fields = ['Date Time', 'Price per gram', 'Selling price per gram']
    with open(filename, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(fields)


def add_row(row: list, filename=FILE_NAME):
    """Adds row in csv"""

    with open(filename, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def scrap():
    """Scraps the data and saves it in the csv"""

    try:
        price_per_gm, selling_price_per_gm = get_price()

        row = [datetime.now(), price_per_gm, selling_price_per_gm]
        add_row(row)

    except Exception as err:
        print('There was an error getting data', err)


if __name__ == "__main__":

    if not os.path.exists(os.path.abspath(FILE_NAME)):
        create_csv()

    # run scrap on start
    scrap()

    # schedule scrap
    schedule.every(TIME_INTERVAL).minutes.do(scrap)

    while True:

        schedule.run_pending()
        time.sleep(1)
