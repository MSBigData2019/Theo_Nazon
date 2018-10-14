# coding: utf-8
import requests
import unittest
from bs4 import BeautifulSoup
import re

url_prefix = "https://www.rueducommerce.fr/recherche/ordinateur-portable-"
url_suffix = "?page=1&sort=remise&universe=MC-3540&view=grid"


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "html.parser")
    return soup

def get_pricing_div(url):
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    link_class = "bigPricerFA clearfix"
    pricing_div = soup.find_all("div", class_=link_class)

    return pricing_div

# def extract_pricing_info(divs):
#
#     result_dict = {}
#
#     for div in divs:
#         div.find("span", class_ = "oldPrice").text
#
#         return result_dict




# def aggregate_company_profile_info(company):
#     query = company
#     url_company = get_profile_link(query)
#
#     res = requests.get(url_company)
#     soup = _handle_request_result_and_build_soup(res)
#
#     result_company = {}
#
#     # Populate result with trading value info
#     list_trading_info = get_trading_info(soup)
#     result_company['Stock value'] = list_trading_info[0]
#     result_company['Trading currency'] = list_trading_info[1]
#
#     # Get all data tables from financials profile of company
#     data_tables = soup.find(class_="column1 gridPanel grid8").find_all(class_="dataTable")
#
#     # Populate result with earning info
#     earning_info = data_tables[0].find_all(class_="data")[6].text
#     result_company["Revenue Q4 18'"] = earning_info
#
#     # Populate result with % of shares owned by public institution
#     institutions_owned = data_tables[1].find_all(class_="data")[-3].text
#     result_company["% of Shares owned by Public institutions"] = institutions_owned
#
#     # Populate result with divident yield info by company / industry / sector
#
#     result_company["Divident yield"] = {
#         "Company": data_tables[2].find_all(class_="data")[3].text,
#         "Industry": data_tables[2].find_all(class_="data")[4].text,
#         "Sector": data_tables[2].find_all(class_="data")[5].text
#     }
#
#     return result_company
#
#
# print(aggregate_company_profile_info("airbus"))
# print(aggregate_company_profile_info("lvmh"))
# print(aggregate_company_profile_info("Danone"))





url_hp = "https://www.fnac.com/SearchResult/ResultList.aspx?SCat=0%211&Search=ordinateur+portable+hp&sft=1&sa=0"
url_acer = "https://www.fnac.com/SearchResult/ResultList.aspx?SCat=0%211&Search=ordinateur+portable+acer&sft=1&sa=0"

request = get_pricing_div(url_hp)

print(request[0])
print(len(request))
print("--------------")

class_to_search = "oldPrice"

request_price = request[0].find("span", class_ = class_to_search)

print(request_price.text)

request_price = request[0].find("span", class_ = class_to_search)
