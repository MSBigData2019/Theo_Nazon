# Accept: application/vnd.github.v3+json
import requests
import unittest
from bs4 import BeautifulSoup
import re
import json
import pandas as pd

token = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson3/token.txt", header = None).iloc[0][0]
print(token)
userID = "TNazon"


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def get_top256_commiters():
    list_of_contributors = []
    url = "https://gist.github.com/paulmillr/2657075"
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    css_selector = "tr"
    tab_contributors = soup.find('table').find_all('tr')

    for i in range(1, len(tab_contributors)):
        contributor = tab_contributors[i].find('a').getText()
        list_of_contributors.append(contributor)
    return list_of_contributors


def get_json_data(contributor, page_number):
    url_user = "https://api.github.com/users/" + contributor + "/repos?page=" + str(page_number)
    res = requests.get(url_user, auth = (userID, token))
    response_object = json.loads(res.text)
    return response_object

def get_repository_ranking(user):
    star_counter = 0
    number_of_repos = 0
    page_number = 1

    while len(get_json_data(user, page_number)) > 0:
        response_object = get_json_data(user, page_number)
        number_of_repos += 1
        for repo in response_object:
            star_counter += int(repo['stargazers_count'])
        page_number += 1

    if number_of_repos == 0:
        return 0
    else:
        return star_counter/number_of_repos

def score_and_rank_contributors(list_of_contributors):
    dict_contributor = {}
    print("Building result dictionnary")
    user_number = 0
    for contributor in list_of_contributors:
        print("Getting information on user number "+ str(user_number))
        dict_contributor[contributor] = get_repository_ranking(contributor)
        user_number += 1
    df = pd.DataFrame.from_fict(dict_contributor)
    return df.sort()


list_top_contributors = get_top256_commiters()
print(score_and_rank_contributors(list_top_contributors))




# https://api.github.com/users/octocat/repos