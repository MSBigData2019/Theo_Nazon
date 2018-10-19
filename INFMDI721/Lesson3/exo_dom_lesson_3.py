# Accept: application/vnd.github.v3+json
import requests
import unittest
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time


token = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson3/token.txt", header = None).iloc[0][0]
print(token)


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
    # list_of_contributors = list(map(lambda x : x.find('a').getText()), tab_contributors)
    for i in range(1, len(tab_contributors)):
        contributor = tab_contributors[i].find('a').getText()
        list_of_contributors.append(contributor)
    return list_of_contributors


def url_API_format(contributor, page_number):
    return "https://api.github.com/users/" + contributor + "/repos?page=" + str(page_number)



def get_json_data(contributor, page_number):
    url_user = url_API_format(contributor, page_number)
    headers = {'Authorization': 'token {}'.format(token)}
    while True:
        res = requests.get(url_user, headers=headers)
        if res.status_code == 200:
            response_object = json.loads(res.text)
            break
        else:
            time.sleep(5)
    return response_object

def get_repository_ranking(user):
    star_counter = 0
    number_of_repos = 0
    page_number = 1

    while len(get_json_data(user, page_number)) > 0:
        response_object = get_json_data(user, page_number)
        number_of_repos += 1
        # star_counter += list(map(lambda x : x['stargazers_count']), response_object).sum()
        for repo in response_object:
            star_counter += repo['stargazers_count']
        page_number += 1

    if number_of_repos == 0:
        return 0
    else:
        return star_counter/number_of_repos

def score_and_rank_contributors(list_of_contributors):
    rated_contributors = pd.DataFrame(columns=['Contributors', 'Average Stars'])
    print("Building result dictionnary")
    user_number = 0
    # map(lambda x : rated_contributors.append({"Contributor": x, "Average Stars": get_repository_ranking(x)}, ignore_index=True), list_of_contributors)
    for contributor in list_of_contributors:
        print("Getting information on user number " + contributor)
        rated_contributors = rated_contributors.append({"Contributor": contributor, "Average Stars": get_repository_ranking(contributor)}, ignore_index=True)
        user_number += 1
    return rated_contributors.sort_values(['Average Stars'], ascending = False)


list_top_contributors = get_top256_commiters()
print(score_and_rank_contributors(list_top_contributors))