from bs4 import BeautifulSoup
import requests
import re
import pandas
import numpy

website_prefix = 'https://www.reuters.com/finance/stocks/financial-highlights/';

def get_element_in_table(soup1, name, row, col):
    title = soup1.find('h3', text=re.compile(name));
    table = title.parent.findNext('div').findChild('table');
    return table.findChildren('tr')[row].findChildren('td')[col].text;

def get_stock_price(soup1):
    return soup1.find('div', class_ = 'sectionQuote nasdaqChange').findChildren('span')[1].text.strip();

def get_stock_price_change(soup1):
    div = soup1.find('div', class_ = 'sectionQuote priceChange');
    return div.findChild('span', text=re.compile(r'.*[0-9]%.*')).text.strip();

def get_financial_results(name):
    
    financial_results = [];    
    res = requests.get(website_prefix + name);
    if res.status_code == 200:
        html_doc =  res.text;
        soup = BeautifulSoup(html_doc,"html.parser");
    
        financial_results.append(get_element_in_table(soup, 'Consensus Estimates Analysis', 2, 2));
        financial_results.append(get_element_in_table(soup, 'Consensus Estimates Analysis', 2, 3));
        financial_results.append(get_element_in_table(soup, 'Consensus Estimates Analysis', 2, 4));
        financial_results.append(get_element_in_table(soup, 'Dividends', 1, 1));
        financial_results.append(get_element_in_table(soup, 'Dividends', 1, 2));
        financial_results.append(get_element_in_table(soup, 'Dividends', 1, 3));
        financial_results.append(get_element_in_table(soup, 'Institutional Holders', 0, 1));
        financial_results.append(get_stock_price(soup));
        financial_results.append(get_stock_price_change(soup));
        
    return financial_results;
   
def show_results(names) :
    results = [];
    for name in names :
        results.append(get_financial_results(name))
    ar = numpy.array(results);
    index = names;
    columns = ['sales_mean', 'sales_high', 'sales_low', 'dividend_compagny', 'dividend_industry', 'dividend_sector', 'institutional_shares', 'price', 'price_change'];
    df = pandas.DataFrame(ar, index = index, columns = columns);
    return df;

print(show_results(['DANO.PA', 'AIR.PA', 'LVMH.PA']))