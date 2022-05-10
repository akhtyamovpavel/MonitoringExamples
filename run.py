import os
import logging
import time
import unicodedata
import graphyte

from datetime import datetime

from selenium import webdriver
from influxdb import InfluxDBClient
from bs4 import BeautifulSoup

logging.getLogger().setLevel(logging.INFO)

GRAPHITE_HOST = 'graphite'
INFLUX_HOST = 'influxdb'
BASE_URL = 'https://yandex.ru/'

CURRENCIES = {
    'USD': 'usd',
    'EUR': 'euro',
    'USD MOEX': 'usd',
    'EUR MOEX': 'euro',
    'Нефть': 'oil'
}

def parse_yandex_page(page):
    currency_blocks = page.findAll('div', {'class': 'inline-stocks__item'})

    currencies = []
    for block in currency_blocks:
        currency_utf8 = block.find('a', {'class': 'home-link'}).text
        currency = unicodedata.normalize("NFKD", currency_utf8)
        value = float(block.find('span', {
            'class': 'inline-stocks__value_inner'
        }).text.replace(',', '.'))

        currencies.append((CURRENCIES[currency], value))
    return currencies


GRAPHITE_HOST = 'graphite'

def send_metrics(currencies):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='currencies')
    for currency in currencies:
        sender.send(currency[0], currency[1])


def send_influx(currencies):
    print(f"send_influx: {currencies}")
    client = InfluxDBClient(host=INFLUX_HOST, port=8086)
    client.create_database('pyexample')
    influx_body = []
    metric_time = datetime.now().isoformat()
    for cur_tittle, cur_value in currencies:
        influx_body.append({
            "measurement": "currencies",
            "tags": {
                "tittle": cur_tittle,
            },
            "time": metric_time,
            "fields": {
                "value": cur_value
            }
        })
    client.write_points(influx_body, database='pyexample')


def main():

    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
    )

    driver.get('https://yandex.ru')
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    metric = parse_yandex_page(soup)
    send_metrics(metric)
    send_influx(metric)


    logging.info('Accessed %s ..', BASE_URL)
    logging.info('Page title: %s', driver.title)
    driver.quit()

if __name__ == '__main__':
    main()
