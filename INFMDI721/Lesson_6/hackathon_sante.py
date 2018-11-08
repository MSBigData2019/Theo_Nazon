# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import difflib
from sklearn import preprocessing
import matplotlib.pyplot as plt
desired_width = 320
pd.set_option('display.width', desired_width)

####################################################
############ DATA LOADING / PREPROCESSING ##########
####################################################

print("--------------------------------------")
print("### LOADING DATA & PROCESSING DATA ###")
print("--------------------------------------")

#----------------------------------------#
# Number of practicioners by departement #
#----------------------------------------#

effectif_by_dpt_by_age = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/RPPS/effectif_par_departement.csv", encoding='latin-1', skiprows=[0,1,2,3,5])
effectif_by_dpt_by_age.melt(id_vars=["Unnamed: 0", "AGE"], value_vars=["Ensemble tous âges confondus", "Moins de 30 ans", "Entre 30 et 34 ans", "Entre 35 et 39 ans", "Entre 40 et 44 ans", "Entre 45 et 49 ans", "Entre 50 et 54 ans", "Entre 55 et 59 ans", "Entre 60 et 64 ans", "Entre 65 et 69 ans", "70 ans et plus"])

effectif_by_dpt = effectif_by_dpt_by_age[["Unnamed: 0", "AGE", "Ensemble tous âges confondus"]]

effectif_columns = ["zone", "specialite", "effectif"]

effectif_by_dpt.columns = effectif_columns

effectif_by_dpt["dpt_number"] = effectif_by_dpt["zone"].str.split(" ").str.get(0)

#----------------------------------------#
#------- Population by departement -------#
#----------------------------------------#

pop_insee_init = pd.read_excel("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/insee_pop.xls", sheet_name=1, skiprows=4)
pop_insee = pop_insee_init[pop_insee_init.columns[0:8].tolist()]

#----------------------------------------#
#------- Population by departement -------#
#----------------------------------------#

# Densite #

df_dens_manual = pd.merge(effectif_by_dpt, pop_insee, left_on="dpt_number", right_on="departement_number")


def density_young(row):
    result = 100000 * row["effectif"] / row["0 à 19 ans"]
    return result


def density_middle(row):
    result = 100000 * row["effectif"] / (row["20 à 39 ans"] + row["40 à 59 ans"])
    return result


def density_old(row):
    result = 100000 * row["effectif"] / (row["60 à 74 ans"] + row["75 ans et plus"])
    return result


def density_all(row):
    result = 100000 * row["effectif"] / row["Total"]
    return result

#####
## Densite en practicien par 100,000 habitants
df_dens_manual["dens_young"] = df_dens_manual.apply(density_young, axis=1)
df_dens_manual["dens_middle"] = df_dens_manual.apply(density_middle, axis=1)
df_dens_manual["dens_old"] = df_dens_manual.apply(density_old, axis=1)
df_dens_manual["dens_total"] = df_dens_manual.apply(density_all, axis=1)

df_dens_clean = df_dens_manual.drop(
    ["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 74 ans", "75 ans et plus", "Total"],
    inplace=False,
    axis=1)

#----------------------------------------#
#------- Revenue data by departement -------#
#----------------------------------------#

revenue_med_by_dpt = pd.read_excel("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/insee_rev.xls", sheet_name="Données des cartes", skiprows=3)

columns_revenue = ["dpt_number", "dpt_name", "median_revenue", "D9/D1", "poverty_rate", "share_subsidied_revenue"]

revenue_med_by_dpt.columns = columns_revenue

#--------------------------------------------#
#------- CONCATENATING SOCIO-DEMO DATA-------#
#--------------------------------------------#

df_socio_demo = pd.merge(df_dens_clean, revenue_med_by_dpt, left_on="dpt_number", right_on="dpt_number")

#---------------------------------------------------------#
#------- Charged fees by population by departement -------#
#---------------------------------------------------------#


## --- Data Loading Begin --- ##

# Load Excel File
xls_path_honoraire = "/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/Honoraires_totaux_des_professionnels_de_sante_par_departement_en_2016.xls"
excel_file = pd.ExcelFile(xls_path_honoraire)

# Extract sheet names
sheet_names = excel_file.sheet_names

# Iterate over sheet name to extract data in separate DataFrame
dict_honoraire = {}
column_names = ["specialite", "department", "effectifs", "hono_sans_depass", "depass", "deplacement", "total_hono"]
for sheet in sheet_names:
    dict_honoraire[sheet] = pd.read_excel(xls_path_honoraire, sheet_name=sheet)
    if dict_honoraire[sheet].columns.size == 7:
        dict_honoraire[sheet].columns = column_names

df_hono_global = pd.concat([dict_honoraire['Spécialistes'], dict_honoraire["Généralistes et MEP"], dict_honoraire["Dentistes et ODF"], dict_honoraire["Sages-femmes"]], ignore_index=True)

df_hono_global.replace("nc", np.nan, inplace=True)
df_hono_global.dropna(inplace=True)

## --- Data Loading End --- ##

## --- Data Processing Begin --- ##

# Adding column that will allow to match tabs using practicioner specialty
# Using difflib matching function at 60%, keeping the best match

# Creating unique list of speciality from
unique_spe_from_densite = df_dens_clean["specialite"].unique()

# Cleaning specialite columns from df_hono_global (it contains "DD- " before any names
df_hono_global["specialite"] = df_hono_global["specialite"].str[4:]

# Matching specialty columns
df_hono_global["spe_matched"] = df_hono_global["specialite"].apply(lambda x : difflib.get_close_matches(x, unique_spe_from_densite, n=1, cutoff=0.6))


# Cleaning output columns for unmatch + flattening result (which is output as array)
df_hono_global["spe_matched_cleaned"] = df_hono_global.spe_matched.apply(lambda x : np.nan if len(x)==0 else x[0])

# Dropping columns initially output from difflib get_close_match work
df_hono_global.drop("spe_matched", axis=1, inplace=True)

# CHECK MATCHING #
df_tmp = df_hono_global[["spe_matched_cleaned", "specialite"]]
df_checking = df_tmp.drop_duplicates()

print("##### Tab de correspondance specialites #####")
print(df_checking)
print("#####################################")

## Departement -> Extracting department number from initial column
df_hono_global["dpt_number"] = df_hono_global["department"].str.split("-").str.get(0)

## Grouping final DataFrame by specialty x department after matching work has been finalized

# Defining aggregating functions to define how columns will be aggregated in the groupby
aggregation_functions = {'effectifs': 'sum', 'hono_sans_depass': 'sum', 'depass': 'sum', 'deplacement': 'sum',  'total_hono': 'sum'}

# Grouping dataframe
df_honoraire = df_hono_global.groupby(["dpt_number", "spe_matched_cleaned"]).aggregate(aggregation_functions)

## --- Data Processing End --- ##

#---------------------------------------------------------#
#------------ MERGING DATAFRAMES FOR ANALYSIS ------------#
#---------------------------------------------------------#

## Merging of the fees DataFrame with socio-demo DataFrame using dpt_number and specialty columns
df_merged = pd.merge(df_socio_demo, df_hono_global, how='left', left_on=['specialite', 'dpt_number'], right_on=['spe_matched_cleaned', 'dpt_number'])

## Cleaning dataframe
df_merged_nona = df_merged.dropna(axis=0, how="any", inplace=False)

# Droping useless columns
df_cleaned = df_merged_nona.drop(
    ["specialite_y", "department", "effectifs", "spe_matched_cleaned", "departement_number"],
    axis=1,
    inplace=False)

####################################################
################## DATA ANALYSIS ###################
####################################################

print("--------------------------------------")
print("### ANALYZING DATA BY DPT & BY SPE ###")
print("--------------------------------------")

## Adding a column calculating % of overcharge as percentage of total fees (excluding transport)

def overcharge_in_pct(row):
    total_fees = row["hono_sans_depass"] + row["depass"]
    if total_fees > 0:
        result = row["depass"] / (row["hono_sans_depass"] + row["depass"])
    else:
        result = np.nan
    return result

# Applying function to calculate overcharge %
df_cleaned["overcharge_per_cent"] = df_cleaned.apply(overcharge_in_pct, axis=1)

# Dropping rows with NaN (=columns with no data on fees)
df_cleaned.dropna(inplace=True)

# Sorting by departement number before final processing
df_cleaned.sort_values("dpt_number", inplace=True)

#####################################################################
################## DATA ANALYSIS - BY DEPARTEMENT ###################
#####################################################################

df_analysis_by_dpt = df_cleaned.set_index("dpt_number")

result_by_dpt = pd.DataFrame(columns=["dpt_number", "correlation_score"])

for index, row in df_analysis_by_dpt.iterrows():
    if index in result_by_dpt["dpt_number"].values:
        continue
    else:
        X_tmp = df_analysis_by_dpt.loc[index, "dens_total"]
        y_tmp = df_analysis_by_dpt.loc[index, "overcharge_per_cent"]
        X_bis_tmp = X_tmp.values.reshape(-1, 1)
        ols_basic_tmp = LinearRegression().fit(X_bis_tmp, y_tmp)
        result_by_dpt = result_by_dpt.append({'dpt_number': index,
                        "correlation_score": ols_basic_tmp.score(X_bis_tmp, y_tmp)},
                       ignore_index=True)

result_by_dpt.sort_values("correlation_score", ascending=False, inplace=True)

#####################################################################
################## DATA ANALYSIS - BY SPECIALTY #####################
#####################################################################

df_analysis_by_spe = df_cleaned.set_index("specialite_x")

aggregation_functions_bis = {'effectif': 'sum', 'hono_sans_depass': 'sum', 'depass': 'sum', 'deplacement': 'sum',  'total_hono': 'sum'}

# Grouping dataframe
df_analysis_by_spe = df_analysis_by_spe.reset_index()
df_analysis_by_spe = df_analysis_by_spe.groupby(["specialite_x", "dpt_number", "dpt", "dens_young", "dens_middle", "dens_old", "dens_total", "dpt_name", "median_revenue", "D9/D1", "poverty_rate", "share_subsidied_revenue"]).aggregate(aggregation_functions_bis)

df_analysis_by_spe["overcharge_per_cent"] = df_analysis_by_spe.apply(overcharge_in_pct, axis=1)

df_analysis_by_spe = df_analysis_by_spe.reset_index()
df_analysis_by_spe = df_analysis_by_spe.set_index("specialite_x")

result_by_spe_single = pd.DataFrame(columns=["specialite", "correlation_score", "sample_size"])
result_by_spe_multi = pd.DataFrame(columns=["specialite", "correlation_score", "sample_size"])



for index, row in df_analysis_by_spe.iterrows():
    if index in result_by_spe_multi["specialite"].values:
        continue
    else:
        X_tmp = df_analysis_by_spe.loc[index, ["dens_total", "median_revenue", "D9/D1"]]
        y_tmp = df_analysis_by_spe.loc[index, "overcharge_per_cent"]
        if isinstance(X_tmp, pd.Series):
            result_by_spe_multi = result_by_spe_multi.append(
                {'specialite': index,
                 "correlation_score": np.nan,
                 "sample_size": 0},
                ignore_index=True)
        else:
            X_scaled = preprocessing.scale(X_tmp)
            ols_basic_tmp = LinearRegression().fit(X_scaled, y_tmp)
            result_by_spe_multi = result_by_spe_multi.append(
                {'specialite': index,
                 "correlation_score": ols_basic_tmp.score(X_scaled, y_tmp),
                 "sample_size": X_scaled.shape[0]
                 },
                ignore_index=True)

result_by_spe_multi.sort_values("correlation_score", ascending=False, inplace=True)

for index, row in df_analysis_by_spe.iterrows():
    if index in result_by_spe_single["specialite"].values:
        continue
    else:
        X_tmp = df_analysis_by_spe.loc[index, "median_revenue"]
        y_tmp = df_analysis_by_spe.loc[index, "overcharge_per_cent"]
        if isinstance(X_tmp, np.float64):
            result_by_spe_single = result_by_spe_single.append(
                {'specialite': index,
                 "correlation_score": np.nan,
                 "sample_size": 0},
                ignore_index=True)
        else:
            X_bis_tmp = X_tmp.values.reshape(-1, 1)
            ols_basic_tmp = LinearRegression().fit(X_bis_tmp, y_tmp)
            result_by_spe_single = result_by_spe_single.append(
                {'specialite': index,
                 "correlation_score": ols_basic_tmp.score(X_bis_tmp, y_tmp),
                 "sample_size": X_tmp.shape[0]},
                ignore_index=True)



result_by_spe_single.sort_values("correlation_score", ascending=False, inplace=True)

#####################################################################
# DISPLAY
#####################################################################


# print(result_by_dpt)
print(result_by_spe_multi)
print("----------------------------------------------------------------------------------------------")
print(result_by_spe_single)


x = result_by_spe_multi["sample_size"]
y = result_by_spe_multi["correlation_score"]
labels = result_by_spe_multi["specialite"]

fig, ax = plt.subplots()
ax.scatter(x, y)

plt.title("Correlation score vs. sample size | by specialty")
plt.ylabel("Correlation score overcharge vs. density")
plt.xlabel("Sample size to calculate correlation score")

for i, txt in enumerate(labels):
    if x[i] > x.mean() and y[i] > y.mean():
        ax.annotate(txt, (x[i], y[i]))

plt.show()