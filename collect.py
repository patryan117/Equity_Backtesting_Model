import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from time import mktime
import os
import time
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))


# Cookie/crum workaround for yahoo fiannce developed by MAIK ROSENHEINRICH at https://maikros.github.io/yahoo-finance-python/
# Micro cap biotech stock listings found at http://investsnips.com/list-of-publicly-traded-micro-cap-diversified-biotechnology-and-pharmaceutical-companies/


def main():
    start_time = time.time()
    get_mid_cap_stock_data()

    print("\n--- %s seconds ---" % (time.time() - start_time))
    # convert_csv_files_to_dfs()



# def convert_csv_files_to_dfs():
#     for filename in os.listdir(dir_path + "/data/"):
#         if filename.endswith(".csv"):
#             file_loc = os.path.join(dir_path, 'relative/path/to/file/you/want')
#             print(filename)
#             df = pd.read_csv(dir_path + "/data/" + filename)
#             print("df sucessfuly converted")
#             # df.to_pickle('testpickle.pkl')
#             # print("pickle saved!")


def get_mid_cap_stock_data():

    print("Retrieving CSV files of Micro-Cap Biotech Stocks...")

    x = 0
    while x != len(micro_cap_list):
        if load_csv_data(micro_cap_list[x]) == False:
            print(micro_cap_list[x], " retrieval failed... re-trying (", len(micro_cap_list)-x, ") remaining.")
            x = x

        if load_csv_data(micro_cap_list[x]) == True:
            print(micro_cap_list[x], " retrieval successful: (",len(micro_cap_list)-x, ") remaining.")
            x = x + 1



    print("\nAll Mid-Cap Biotech Datasets Retrieved Successfully")
    print(len(micro_cap_list), " Datasets Retrieved")





def _get_crumbs_and_cookies(stock):

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

    datum = datetime.strptime(date, '%d-%m-%Y')
    return int(mktime(datum.timetuple()))


def load_csv_data(stock, interval='1d', day_begin='01-01-2010', day_end='01-09-2018'):

    day_begin_unix = convert_to_unix(day_begin)
    day_end_unix = convert_to_unix(day_end)
    header, crumb, cookies = _get_crumbs_and_cookies(stock)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with requests.session():
        url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
              '{stock}?period1={day_begin}&period2={day_end}&interval={interval}&events=history&crumb={crumb}' \
            .format(stock=stock, day_begin=day_begin_unix, day_end=day_end_unix, interval=interval, crumb=crumb)

        website = requests.get(url, headers=header, cookies=cookies)
        file = open(dir_path + "/data/" + str(stock)+".csv", 'w')
        file.write(website.text)
        file.close()


        if "Invalid cookie" in website.text:
            return False

        else:
            return True



global  micro_cap_list
micro_cap_list = [ "ALDX", "BLRX", "CRMD", "KDMN", "KALV", "KMDA", "MDGL", "MGEN", "PTGX", "RETA", "TRVN", "CDTX", \
                       "MTNB", "NBRV", "KIN", "XOMA", "CMRX", "CTRV", "NNVC", "CDXS", "PFNX", "ATNM", "AGLE", "AFMD", \
                       "ALRN", "AVEO", "BPTH", "BTAI", "CASI", "CBMG", "CGEN", "CTIC", "DFFN", "ECYT", "FBIO", "GALT", \
                       "GNPX", "GTXI", "IMDZ", "IMGN", "IMMP", "INFI", "KURA", "LPTX", "MEIP", "MRTX", "NK", "ONS", \
                       "PIRS", "RNN", "SLS", "SRNE", "STML", "SNSS", "SNDX", "TOCA", "TCON", "TRIL", "VBLT", "VSTM",  \
                       "ZYME", "ZYNE", "AST", "CYAD", "CUR", "PSTI", "VCEL", "AVXL", "AXSM", "NTEC", "NERV", "TTNP", \
                       "TENX", "KRYS", "MNKD", "NEPT", "ADVM", "AGTC", "CLSD", "IMMY", "NBY", "OCUL", "OHRP", "OPHT", \
                       "OVAS", "RDHL", "PLX", "GNMX", "CAPR", "GEMP", "SELB", "CALA", "ADMA", "ASNS", "CFRX", "DVAX", \
                       "SGMO", "SMMT", "MTFB", "SPRO", "AMPE", "ABUS", "ARWR", "CNAT", "DRNA", "GLMD", "VTL", "ALNA", \
                       "CBAY", "SYN", "BCLI", "EDGE", "MNOV", "OVID", "FLKS", "DRRX", "ABEO", "AKTX", "LIFE", "CATB", \
                       "CPRX", "CHMA", "EIGR", "FATE", "NVLN", "RGLS", "RCKT", "SBBP", "QURE", "XENE", "ATHX", "PRQR",\
                       "PTI", "PULM", "VRNA", "ARCT", "GLYC", "NYMX", "SPHS", "URGN", "GNCA", "VBIV", "SBPH", "VVUS", \
                       "ZFGN", "OBSV", "PTN", "MDWD"]


if __name__ == "__main__":
    main()

