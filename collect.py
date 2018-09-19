import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from time import mktime
import csv
import os
import sys





def main():
    test = load_csv_data("MRTX")
    print((test))




def _get_crumbs_and_cookies(stock):
    """
    get crumb and cookies for historical data csv download from yahoo finance
    parameters: stock - short-handle identifier of the company
    returns a tuple of header, crumb and cookie
    """

    url = 'https://finance.yahoo.com/quote/{}/history'.format(stock)
    with requests.session():
        header = {'Connection': 'keep-alive',
                  'Expires': '-1',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                  }

        website = requests.get(url, headers=header)
        soup = BeautifulSoup(website.text, 'lxml')
        crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))

        return (header, crumb[0], website.cookies)


def convert_to_unix(date):
    """
    converts date to unix timestamp
    parameters: date - in format (dd-mm-yyyy)
    returns integer unix timestamp
    """
    datum = datetime.strptime(date, '%d-%m-%Y')

    return int(mktime(datum.timetuple()))


def load_csv_data(stock, interval='1d', day_begin='01-01-2016', day_end='01-09-2018'):
    """
    queries yahoo finance api to receive historical data in csv file format

    parameters:
        stock - short-handle identifier of the company
        interval - 1d, 1wk, 1mo - daily, weekly monthly data
        day_begin - starting date for the historical data (format: dd-mm-yyyy)
        day_end - final date of the data (format: dd-mm-yyyy)

    returns a list of comma seperated value lines
    """

    day_begin_unix = convert_to_unix(day_begin)
    day_end_unix = convert_to_unix(day_end)
    header, crumb, cookies = _get_crumbs_and_cookies(stock)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    with requests.session():
        url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
              '{stock}?period1={day_begin}&period2={day_end}&interval={interval}&events=history&crumb={crumb}' \
            .format(stock=stock, day_begin=day_begin_unix, day_end=day_end_unix, interval=interval, crumb=crumb)

        website = requests.get(url, headers=header, cookies=cookies)
        file = open(dir_path + "/data/" + str(stock)+".csv", 'w')
        file.write(website.text)
        file.close()
        return website.text.split('\n')[:-1]




if __name__ == "__main__":
    main()