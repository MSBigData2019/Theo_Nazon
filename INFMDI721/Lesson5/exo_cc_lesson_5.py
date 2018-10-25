import requests
import unittest
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time
import pandas as pd
desired_width = 320
pd.set_option('display.width', desired_width)


url_search = "https://open-medicaments.fr/api/v1/medicaments?query=paracetamol&limit=100"
res = requests.get(url_search)
response_object = json.loads(res.text)

df = pd.DataFrame(response_object)

reg = r"([\D]*)(\d+)(.*),([\w\s]*)"
string = "PARACETAMOL ZYDUS 500 mg, gélule"
match = re.search(reg, string)



df = df["denomination"].str.extract(reg)

df["factor"] = 1000
df["factor"] = df["factor"].where(df[2].str.strip() == "g", 1)

df["dosage"] = df[1].fillna(0).astype(int) * df["factor"]
# df['type'] = df['denomination'].str.extract(reg)

# df["company"] = df["denomination"].str.split(" ").str[1]
# df["dosage"] = df["denomination"].str.split(" ").str[2]

print(df)

