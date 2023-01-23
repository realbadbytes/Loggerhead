import os
import csv

# https://www.nasdaq.com/market-activity/stocks/screener

def load_data():
    """ Parse all symbols from .csv file containing all stock symbols for a particular industry.

    :param industry: User-provided industry string
    :returns: List of symbols in a particular industry
    """
    market_data = {}
    directory = os.fsencode('industry_data')
    for file in os.listdir(directory):
        with open('industry_data/' + file.decode('utf-8')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                market_data[row['Symbol']] = row
    return market_data

if __name__ == '__main__':
    market_data = load_data()
    print(market_data['AAPL'])