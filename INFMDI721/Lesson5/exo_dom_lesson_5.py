# Accept: application/vnd.github.v3+json
import requests
import unittest
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time
desired_width = 320
pd.set_option('display.width', desired_width)

url = "https://www.lacentrale.fr/cote-voitures-renault-zoe--2017-.html"
url_search = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF%2CFR-PAC%2CFR-NAQ"
url_sellers = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF%2CFR-NAQ%2CFR-PAC"

#########################################
########### SUPPORT FUNCTIONS ###########
#########################################

def _create_request_and_generate_soup(url):
    res = requests.get(url)
    if res.status_code == 200:
        html_doc = res.text
        soup = BeautifulSoup(html_doc, "html.parser")
    return soup

def explode_df(df):
    df_exploded = df.list_of_urls.apply(pd.Series)\
        .stack()\
        .reset_index(level=1, drop=True)\
        .to_frame('list_of_urls')
    return df_exploded


#########################################
########### SUPPORT FUNCTIONS ###########
#########################################

#########################################
### ARGUS DATABASE ###
#########################################

def get_links_for_argus():
    url_df = pd.DataFrame()
    list_links = []
    years = [2012, 2013, 2014, 2015, 2016, 2017, 2018]
    for year in years :
        url = "https://www.lacentrale.fr/cote-voitures-renault-zoe--{}-.html".format(year)
        soup = _create_request_and_generate_soup(url)
        div_result = soup.findAll(class_ = "listingResultLine")
        list_links = list(map(lambda x : x.find("a")["href"], div_result))
        url_df = url_df.append({"year" : int(year), "list_of_urls" : list_links}, ignore_index=True)

    url_df.set_index(['year'], inplace=True)
    return url_df

def extract_price_info(df):
    url_base = "https://www.lacentrale.fr/{}".format(df["list_of_urls"])
    print(url_base)
    soup = _create_request_and_generate_soup(url_base)
    df['detailed_model'] = soup.find(class_ = "sizeC clear txtGrey7C sizeC").text.strip()
    df['quote'] = soup.find(class_ = "jsRefinedQuot").text.strip()
    print("Scraping current url " + url)
    time.sleep(4)
    return df

#########################################
### ARGUS DATABASE ###
#########################################

#########################################
### SELLER DATABASE ###
#########################################

def get_cars_on_sale_info_from_search_page(page_number):
    time.sleep(2)
    url_search = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&options=&page={}&regions=FR-IDF%2CFR-PAC%2CFR-NAQ".format(page_number)
    soup_search = _create_request_and_generate_soup(url_search)
    car_profile_lists = soup_search.find_all(class_ = "adContainer")

    list_of_cars_processed = list(map(lambda x : extract_info_per_car(x), car_profile_lists))
    return list_of_cars_processed


def consolidated_info_cars_on_sale():
    consolidated_list_cars = []
    page_number = 1
    limit_reached = False
    while not limit_reached:
        returned_list_from_scrapped_page = get_cars_on_sale_info_from_search_page(page_number)
        if len(returned_list_from_scrapped_page) > 0:
            page_number += 1
            consolidated_list_cars = consolidated_list_cars + returned_list_from_scrapped_page
        else :
            limit_reached = True

    sales_info = pd.DataFrame(consolidated_list_cars)
    sales_info = format_dataframe(sales_info)
    return sales_info

def consolidated_info_cars_on_sale_short():
    consolidated_list_cars = []
    page_number = 1
    returned_list_from_scrapped_page = get_cars_on_sale_info_from_search_page(page_number)
    consolidated_list_cars = consolidated_list_cars + returned_list_from_scrapped_page
    sales_info = pd.DataFrame(consolidated_list_cars)
    sales_info = format_dataframe(sales_info)
    return sales_info

#
# def consolidated_info_cars_on_sale():
#     url_search = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF%2CFR-PAC%2CFR-NAQ"
#     soup_search = _create_request_and_generate_soup(url_search)
#     car_profile_lists = soup_search.find_all(class_ = "adContainer")
#
#     list_of_car_profiles_processed = list(map(lambda x : extract_car_info(x), car_profile_lists))
#     sales_info = pd.DataFrame(list_of_car_profiles_processed)
#     sales_info.columns = ["model_long", "type_seller", "year", "km", "price", "phone_number", "link"]
#     return sales_info

dict_of_classes_for_car_profiles = {
    "model"             : "version txtGrey7C noBold",
    "type_of_seller"    : "txtBlack typeSeller hiddenPhone",
    "year"              : "fieldYear",
    "mileage"           : "fieldMileage",
    "quotation"         : "fieldPrice sizeC"
}


def get_phone_number(url_suffix):
    url_offer = "https://www.lacentrale.fr/" + url_suffix
    soup = _create_request_and_generate_soup(url_offer)
    phone_number = soup.find(class_ = "phoneNumber1").text
    return phone_number


def extract_info_per_car(car_profile):
    info_per_car_format_list = []

    # On itere sur la liste des informations a recuperer, que l'on place dans liste
    for key in dict_of_classes_for_car_profiles.keys():
        new_element = car_profile.find(class_= dict_of_classes_for_car_profiles[key]).text if car_profile.find(class_= dict_of_classes_for_car_profiles[key]) is not None else "n.a."
        info_per_car_format_list.append(new_element)

    # Ajout du lien vers l'annonce de la voiture + numero de telephone #
    url_offer = car_profile.find("a")['href']
    info_per_car_format_list.append(get_phone_number(url_offer))
    info_per_car_format_list.append(url_offer)

    return info_per_car_format_list


def format_dataframe(df):
    df.columns = ["model_long", "type_seller", "year", "km", "price", "phone_number", "link"]
    df["phone_number"] = df["phone_number"].str.replace(r"\D+", "").astype("int64")
    df["price"] = df["price"].str.replace(r"\D+", "").astype("int64")
    df["km"] = df["km"].str.replace(r"\D+", "").astype("int64")
    df["model"] = df["model_long"].str.split(" ").str[0]

    return df

#########################################
### SELLER DATABASE ###
#########################################


def get_argus_df():
    pd_links = get_links_for_argus()
    df_argus = explode_df(pd_links)
    df_argus = df_argus.apply(extract_price_info, axis=1)
    df_argus["model"] = df_argus.detailed_model.str.split(" ").str.get(0)
    df_argus["quote"].str.replace(" ", "").astype("int64")

    return df_argus

df_argus = get_argus_df()
# df_argus["quote"] = df_argus["quote"].str.replace(r"\D+", "").astype("int64")

df_cars_on_sale = consolidated_info_cars_on_sale_short()


# df_mean = df_argus.groupby(['year', "model"])["quote"].mean()
# df_mean.reset_index()
# df_cars_on_sale = df_cars_on_sale.merge(df_mean,on='model',how='left')


print(df_cars_on_sale.head())