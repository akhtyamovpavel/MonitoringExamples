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
    'USD ЦБ': 'usd',
    'EUR': 'euro',
    'EUR ЦБ': 'euro',
    'USD MOEX': 'usd',
    'EUR MOEX': 'euro',
    'Нефть': 'oil'
}

def parse_yandex_page(page):
    currency_blocks = page.findAll('a', {'class': 'stocks__item'})

    currencies = []
    for block in currency_blocks:
        currency_utf8 = block.find('div', {'class': 'stocks__item-title'}).text
        currency = unicodedata.normalize("NFKD", currency_utf8)
        value = float(block.find('div', {
            'class': 'stocks__item-value'
        }).text.replace(',', '.').replace('₽', '').replace('$', '').strip())

        currencies.append((CURRENCIES[currency], value))
    return currencies


def send_metrics(currencies):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='currencies')
    for currency in currencies:
        sender.send(currency[0], currency[1])


def send_influx(currencies):
    print(f"send_influx: {currencies}")
    client = InfluxDBClient(host=INFLUX_HOST, port=8086)
    influx_body = []
    metric_time = datetime.now().isoformat()
    for cur_title, cur_value in currencies:
        influx_body.append({
            "measurement": "currencies",
            "tags": {
                "title": cur_title,
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
    logging.info('Accessed %s ..', BASE_URL)
    logging.info('Page title: %s', driver.title)
    driver.quit()

    metric = parse_yandex_page(soup)
    send_metrics(metric)
    send_influx(metric)


if __name__ == '__main__':
    main()
