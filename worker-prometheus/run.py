import os
import logging
import time
import unicodedata


from selenium import webdriver
from bs4 import BeautifulSoup
from prometheus_client import start_http_server, Summary, Gauge


logging.getLogger().setLevel(logging.INFO)

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


gauges = {
    'oil': Gauge('oil', 'Oil price at MOEX'),
    'euro': Gauge('euro', 'Euro price at MOEX'),
    'usd':  Gauge('usd', 'Usd price at MOEX'),
}

class Driver:
    def __init__(self):

        self.browser = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
        )

def main():
    driver = Driver()

    start_http_server(8000)
    while True:
        driver.browser.get('https://yandex.ru')
        time.sleep(5)
        
        logging.info('Accessed %s ..', BASE_URL)
        logging.info('Page title: %s', driver.browser.title)

        html = driver.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        metrics = parse_yandex_page(soup)
        for metric_name, metric_value in metrics:
            logging.info(f'{metric_name}: {metric_value}')
            gauges[metric_name].set(metric_value)
        
        time.sleep(30)

if __name__ == '__main__':
    main()
