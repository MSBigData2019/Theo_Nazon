import requests
import json
import pandas as pd

df = pd.read_excel("/home/theo/Dropbox/list_cities.xls", headers=None)[:10]
df["Ville"] = df["Ville"] + ", France"

list_of_cities_for_API = "|".join(df["Ville"])
api_key = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson4/api_key.txt", header = None).iloc[0][0]


def get_distance_between_two_cities(list_of_cities_for_API):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&key={}".format(list_of_cities_for_API, list_of_cities_for_API, api_key)
    res = requests.get(url)
    response_object = json.loads(res.text)
    distances = list(map(lambda x : list(map(lambda y : y['distance']['text'], x['elements'])), response_object['rows']))
    distance_matrix = pd.DataFrame(distances, columns=df["Ville"], index=df["Ville"])
    return distance_matrix

print(get_distance_between_two_cities(list_of_cities_for_API))
