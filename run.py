import logging
import graphyte

from datetime import datetime

from influxdb import InfluxDBClient
import requests
from xml.etree import ElementTree


logging.getLogger().setLevel(logging.INFO)

GRAPHITE_HOST = 'graphite'
INFLUX_HOST = 'influxdb'
#BASE_URL = 'https://yandex.ru/'

BASE_URL = 'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{}.xml'

TICKERS = ['SBERP', 'SBER', 'GAZP']


def send_metrics(currencies):
    sender = graphyte.Sender(
        GRAPHITE_HOST, prefix='stocks'
    )
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


def get_metrics():
    results = []
    for ticker in TICKERS:
        response = requests.get(BASE_URL.format(ticker))
        if response.status_code != 200:
            continue

        tree = ElementTree.fromstring(response.text)
        element = tree.findall('./data[@id="marketdata"]/rows/row[@BOARDID="TQBR"]')[0]
        results.append((ticker, float(element.attrib['LAST'])))

    return results

    
def main():

    metric = get_metrics()
    send_metrics(metric)
    send_influx(metric)


if __name__ == '__main__':
    main()
