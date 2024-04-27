import logging
import time
import requests
from xml.etree import ElementTree

from prometheus_client import start_http_server, Histogram


logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{}.xml'

TICKERS = ['SBERP', 'SBER', 'GAZP']

histograms = {
    'SBERP': Histogram(
        'sberp_hist_configured', 'SBERP price at MOEX',
        buckets=list(range(290, 330, 5))
    ),
    'SBER': Histogram(
        'sber_hist_configured', 'SBER price at MOEX', 
        buckets=list(range(290, 330, 5))
    ),
    'GAZP': Histogram(
        'gazp_hist_configured', 'GAZP price at MOEX',
        buckets=list(range(150, 200, 5))
    ),
}


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

    start_http_server(8000)
    while True:
        
        metrics = get_metrics()

        for metric_name, metric_value in metrics:
            logging.info(f'{metric_name}: {metric_value}')
            histograms[metric_name].observe(metric_value)
        
        time.sleep(30)

if __name__ == '__main__':
    main()
