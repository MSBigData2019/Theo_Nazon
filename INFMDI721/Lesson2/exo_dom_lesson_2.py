# coding: utf-8
import requests
import unittest
from bs4 import BeautifulSoup
import re

root_url = "https://www.reuters.com"
reuters_search_prefix = "https://www.reuters.com/search/news?blob="
reuters_profil_prefix = "https://www.reuters.com/finance/stocks/financial-highlights/"


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def get_profile_link(query):
    url = reuters_search_prefix + query
    print(url)
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    link_class = "search-stock-ticker"
    link_to_profile = soup.find("div", class_=link_class).find("a").attrs['href']

    url_company_profile = root_url + link_to_profile
    url_company_financials = url_company_profile.replace("overview", "financial-highlights")
    # Retrieve the company code based on href - optionnal
    # company_code = link_to_profile.split('=')[1]
    return url_company_financials


def get_trading_info(soup):
    trading_info = soup.find(class_='sectionQuote nasdaqChange').find(class_="sectionQuoteDetail").find_all("span")
    trading_value = trading_info[1].text.strip()
    trading_currency = trading_info[2].text
    return [trading_value, trading_currency]


def get_divident_yield_info(data_tables):
    divident_yield = {}
    divident_yield["Company"]  = data_tables[2].find_all(class_="data")[3].text
    divident_yield["Industry"] = data_tables[2].find_all(class_="data")[4].text
    divident_yield["Sector"]   = data_tables[2].find_all(class_="data")[5].text
    return divident_yield


def aggregate_company_profile_info(company):
    query = company
    url_company = get_profile_link(query)
    res = requests.get(url_company)
    soup = _handle_request_result_and_build_soup(res)
    result_company = {}

    # Populate result with trading value info
    list_trading_info = get_trading_info(soup)
    result_company['Stock value'] = list_trading_info[0]
    result_company['Trading currency'] = list_trading_info[1]

    # Get all data tables from financials profile of company
    data_tables = soup.find(class_="column1 gridPanel grid8").find_all(class_="dataTable")

    # Populate result with earning info
    earning_info = data_tables[0].find_all(class_="data")[6].text
    result_company["Revenue Q4 18'"] = earning_info

    # Populate result with % of shares owned by public institution
    institutions_owned = data_tables[1].find_all(class_="data")[-3].text
    result_company["% of Shares owned by Public institutions"] = institutions_owned

    # Populate result with divident yield info by company / industry / sector
    result_company["Divident yield"] = get_divident_yield_info(data_tables)

    return result_company


print(aggregate_company_profile_info("airbus"))
print(aggregate_company_profile_info("lvmh"))
print(aggregate_company_profile_info("Danone"))