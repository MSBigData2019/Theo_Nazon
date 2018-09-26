import math as math
import pandas as pd

def product_with_loop(epsilon):
    result = 2
    i = 1
    delta = True
    while(i < math.inf and delta):
        previous = result
        result *= (4 * math.pow(i, 2)) / (4 * math.pow(i, 2) + 1)
        delta = False if result - previous < epsilon else True
        i += 1
    return result


df = pd.read_csv("https://bitbucket.org/portierf/shared_files/downloads/household_power_consumption.txt", usecols=["Date", "Global_active_power", "Sub_metering_1"], sep=";", na_values=[0, "0.000", '?', 'NaN'])
print(df.info())