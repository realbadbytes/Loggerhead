#!/usr/bin/env python
'''Collections of utilities for gathering portfolio and stock data'''

from pprint import pprint
from collections import OrderedDict
import urllib
import requests
import csv
import time

StockMarket = OrderedDict()
Sectors = {'Basic Industries':'bi', 'Capital Goods':'cg', 'Consumer Non-Durables':'nd',
        'Consumer Services':'services', 'Energy':'energy', 'Finance':'fin', 'Health Care':'health',
        'Miscellaneous':'misc', 'Public Utilities':'utils', 'Technology':'tech', 'Transportation':'transport'}

# http://stackoverflow.com/questions/22824230/get-a-file-from-an-aspx-webpage-using-python
# http://www.nasdaq.com/screening/company-list.aspx
# "Symbol","Name","LastSale","MarketCap","ADR TSO","IPOyear","Sector","Industry","Summary Quote"
def get_company_list():
    'Every night pick up list of companies and update db with any new trading companies'
    global StockMarket

    url_nasdaq = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download'
    url_nyse = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download'
    url_amex = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=AMEX&render=download'

    url_bi = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Basic+Industries&render=download'
    url_cg = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Capital+Goods&render=download'
    url_nd = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Consumer+Non-Durables&render=download'
    url_services = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Consumer+Services&render=download'
    url_energy = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Energy&render=download'
    url_fin = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Finance&render=download'
    url_health = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Health+Care&render=download'
    url_misc = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Miscellaneous&render=download'
    url_utils = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Public+Utilities&render=download'
    url_tech = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Technology&render=download'
    url_transport = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?industry=Transportation&render=download'
    #urls = [url_nasdaq, url_nyse, url_amex]
    urls = [url_bi, url_cg, url_nd, url_services, url_energy, url_fin,
            url_health, url_misc, url_utils, url_tech, url_transport]
    for url in urls:
        u = requests.get(url)
        # a better way to read the file
        cr = csv.reader(u.iter_lines())
        for c in cr:
            if len(c) == 10:
                stk = c[0].replace('/','-').replace('^','-P') #cleanup symbol name only '-' allowed, no '/' no '^'
                StockMarket[stk] = {
                        'Name': c[1], 'LastSale': c[2], 'MarketCap': c[3],
                        'IPOyear': c[5], 'Sector': c[6], 'Industry': c[7],
                        'Quote': 'www.finance.yahoo.com/q?s='+c[0], 'Open': 0, 'Hi': 0,
                        'Lo': 0, 'PctChange': '+0.00'
                        }
            #else:
                #print 'Error: Less than 10 cols in csv entry '
                #print c
    # Sort dict by trading symbol
    # https://docs.python.org/2/library/collections.html#collections.OrderedDict
    StockMarket = OrderedDict(sorted(StockMarket.items(), key=lambda t:t[0]))
    # NOTIFICATION: Notify me of any new Sectors!

def dump_initial_charts():
    fnDrawStockTable = '''
function drawStockTable() {
        for(var sector in slist) {
            var slist_html = '';
            if(slist.hasOwnProperty(sector)) {
                for(var stock in slist[sector]) {
                    if(slist[sector].hasOwnProperty(stock)) {
                        var ss = slist[sector][stock];
                        slist_html += '<div class="row-res" id="'+stock+'"><a class="btn btn-'+ss[2]+'" title="'+ss[3]+'" href="http://finance.yahoo.com/q?s='+stock+'" target="_blank"><p class="sybl">'+stock+'</p><p class="price">'+ss[0]+'<br>'+ss[1]+'</p></a></div>'
                    }
                } //for(stock)
            }
            var symbl = '#sector-'+sector;
            $(symbl).html(slist_html);
        } //for(sector)
} //drawStockTable()
    '''
    with open('stock_chart.js', 'w') as f:
        f.write('var slist = {};\n')
        for sector in Sectors:
            f.write('\nslist["'+Sectors[sector]+'"] = {\n')
            for stk in StockMarket:
                if StockMarket[stk]['Sector'] == sector:
                    f.write('\t"'+stk+'":['+StockMarket[stk]['LastSale']+',"+0.00%","primary","'+StockMarket[stk]['Name']+'"],\n')
            f.write('};')
        f.write(fnDrawStockTable)
    f.close()

def fetch_current_quotes():
    'Write latest quotes into a file'
    global StockMarket
    global StockUpdateList

    StockUpdateList = []
    new_url = [stk for stk in StockMarket]
    while len(new_url) != 0:
        if len(new_url) > 199:
            new_url_str = str(new_url[0:199])[1:-1] #using 1:-1 of the str to remove '[' & ']' of the list
            new_url = new_url[199:]
        else:
            new_url_str = str(new_url)[1:-1]
            new_url = []
        # sl1cohg - selects what fields are contained in the csv downloaded from yahoo finance
        # s - symbol; l1 - last sale; c - %change; o - open; h - Day-hi; g - Day-lo
        # http://www.financialwisdomforum.org/gummy-stuff/Yahoo-data.htm
        print 'Getting quotes for:'
        print new_url_str
        yurl = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1p2ohg&e=.csv'
        u = requests.get(yurl % new_url_str)
        cr = csv.reader(u.iter_lines())
        for c in cr:
            if len(c) == 6:
                try:
	                #if StockMarket[c[0]]['LastSale'] != c[1]:
	                StockMarket[c[0]]['LastSale'] = c[1]
	                StockMarket[c[0]]['PctChange'] = c[2]
	                StockMarket[c[0]]['Open'] = c[3]
	                StockMarket[c[0]]['Hi'] = c[4]
	                StockMarket[c[0]]['Lo'] = c[5]
	                StockUpdateList.append(c[0])
                except KeyError:
                    print "Could not find in StockMarket "+c[0]
            else:
                print "Error while updating stocks, yahoo returned"
                print c

def dump_now_charts():
    fnUpdateStockPrices = '''
function updateStockPrices() {
    for(var stock in supdate) {
      if(supdate.hasOwnProperty(stock)){
          var symbl = '#'+stock;
          var newPrice = supdate[stock][0]+"<br>"+supdate[stock][1];
          var newClass = "btn btn-"+supdate[stock][2];
          $(symbl).children("a").children("p.price").html(newPrice);
          /* Change Class http://stackoverflow.com/questions/3452778/jquery-change-class-name */
          $(symbl).children("a").attr("class", newClass);
      }
    }
    /*var t = setTimeout(function(){updateStockPrices()},5000);*/
}
    '''
    with open('update_stocks.js', 'w') as f:
        f.write('var supdate = {\n')
        for stk in StockUpdateList:
            # http://stackoverflow.com/questions/455612/limiting-floats-to-two-decimal-points
            # https://docs.python.org/2/library/string.html#format-specification-mini-language
            last_sale = float("{0:.2f}".format(float(StockMarket[stk]['LastSale']))) 
            pct_change_str = StockMarket[stk]['PctChange'] #float("{0:.2f}".format(float(StockMarket[stk]['PctChange'])))
            try:
                pct_change = float(StockMarket[stk]['PctChange'].replace('%',''))
            except ValueError:
                print "Could not convert PctChange to float " + stk + StockMarket[stk]['PctChange']
            if pct_change > 1:
                color = 'success'
                #pct_change_str = ("+%.2f" % pct_change) + '%'
            elif pct_change > 0:
                color = 'msuccess'
                #pct_change_str = ("+%.2f" % pct_change) + '%'
            elif pct_change < -1:
                color = 'danger'
                #pct_change_str = ("%.2f" % pct_change) + '%'
            else:
                color = 'primary'
                #pct_change_str = ("%.2f" % pct_change) + '%'
            f.write('\t"'+stk+'":['+str(last_sale)+',"'+pct_change_str+'","'+color+'"],\n')
        f.write('};\n')
        f.write(fnUpdateStockPrices)
    f.close()

# http://boto.readthedocs.org/en/latest/s3_tut.html#s3-tut
def push_files_to_s3():
    pass

# Get ETF list
# http://online.wsj.com/mdc/public/page/2_3024-USETFs.html?mod=topnav_2_3021
# http://online.wsj.com/public/resources/documents/USETFs.csv
# Get top 10 holdings
# https://finance.yahoo.com/q/hl?s=VTI
def generate_etfs_table():
    pass


def get_portfolio(filename):
    'Parse a CSV file in the form: symbol,shares,price'
    # list of all companies traded
    # http://www.nasdaq.com/screening/company-list.aspx
    result = []
    f = open(filename)
    for line in f:
        line = line.rstrip()
        symbol, shares, price = line.split(',')
        shares = int(shares)
        price = float(price)
        fields = symbol, shares, price
        result.append(fields)
    f.close()
    return result

def get_quote(symbol):
    'Return a real-time stock quote from yahoo finance'
    url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1c1ohgv&e=.csv'
    u = urllib.urlopen(url % symbol)
    data = u.read()
    return float(data.split(',')[1])

def get_quotes(*symbols):
    'Return a dictionary of real-time stock quotes'
    result = {}
    for symbol in symbols:
        result[symbol] = get_quote(symbol)
    return result

def main_procee():
    # Thread1: Nightly Task
    # Thread2: Latest Quotes
    pass

if __name__ == '__main__':
    #pprint(get_portfolio('notes/stocks.txt'))
    #print get_quote('CSCO')
    #print get_quote('MSFT')
    #print get_quotes('CSCO', 'YHOO', 'MSFT') # -> {'CSCO': 17.1, 'YHOO': 12.5, 'MSFT': 31.1}
    # Call mainthread here
    start_time = time.time()
    get_company_list()
    dump_initial_charts()
    end_time = time.time()
    print '... Generated initial stocks in ...', int(end_time - start_time), ' seconds'
    start_time = time.time()
    fetch_current_quotes()
    dump_now_charts()
    end_time = time.time()
    print '... Generated updated stocks in ...', int(end_time - start_time), ' seconds'