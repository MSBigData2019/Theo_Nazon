# coding: utf-8

import pandas as pd
import numpy as np
import math as m
from sklearn.linear_model import LinearRegression

desired_width = 320

pd.set_option('display.width', desired_width)


df_density = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/RPPS/densite_medecin.csv", encoding='latin-1', skiprows=[0,1,2,3,5])
headers = list(df_density)
headers_reviewed = list(map(lambda x : "type_" + x, headers))
headers_reviewed[0] = "region"
df_density.columns = headers_reviewed
df_density_long = pd.wide_to_long(df_density, i = "region", stubnames = ["type_"], j = "specialite", suffix="\\w+")
print(df_density_long.head())
df_density_long = df_density_long.reset_index()
# df_density.set_index("region", inplace = True, verify_integrity = True)



########
# idx = df_density_long.index.values
# idx_spe = list(map(lambda x : x[1], idx))
# ls = []
# for n in idx_spe:
#     if n not in ls:
#         ls.append(n)
########





print("#################")
print("#################")

effectif_medecin = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/RPPS/effectif_medecin.csv", encoding='latin-1', skiprows=[0,1,2,3,5])
# print(effectif_medecin.head())
# print("#################")
# print("#################")

effectif_medecin_age = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/RPPS/effectif_medecin_tranche_age.csv", encoding='latin-1', skiprows=[0,1,2,3,5])
# print(effectif_medecin_age.head())
# print("#################")
# print("#################")


# Load Excel File
xls_path_honoraire = "/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/Honoraires_totaux_des_professionnels_de_sante_par_departement_en_2016.xls"
excel_file = pd.ExcelFile(xls_path_honoraire)

# Extract sheet names
sheet_names = excel_file.sheet_names

# Iterate over sheet name to extract data in separate DataFrame
dict_honoraire = {}
column_names = ["specialite", "department", "effectifs", "hono_sans_depass", "depass", "deplacement", "total_hono"]
for sheet in sheet_names:
    dict_honoraire[sheet] = pd.read_excel(xls_path_honoraire, sheet_name = sheet)
    if dict_honoraire[sheet].columns.size == 7:
        dict_honoraire[sheet].columns = column_names


# ['Lisez moi', 'Nomenclature des PS', 'Spécialistes', 'Généralistes et MEP', 'Dentistes et ODF', 'Sages-femmes', 'Auxiliaires médicaux', 'Laboratoires']

# ls = ["specialisation"]
# ls + df_sf.columns.tolist()[1:]

df_hono_global = pd.concat([dict_honoraire['Spécialistes'], dict_honoraire["Généralistes et MEP"], dict_honoraire["Dentistes et ODF"], dict_honoraire["Sages-femmes"]], ignore_index = True)

df_hono_global.replace("nc", np.nan, inplace = True)
df_hono_global.dropna(inplace=True)
# list_spe = np.array(df_hono_global["specialite"].unique())
# list_spe.sort()

from difflib import SequenceMatcher
import difflib

def similar(a,b):
    return SequenceMatcher(None, a, b).ratio()

##########
###### TABLEAU HONORAIRE

## Specialisation
# Ajout d'une colonne de correspondance a 60% sur le nom de la specialisation
unique_spe_from_densite = df_density_long["specialite"].unique()
df_hono_global["spe_matched"] = df_hono_global["specialite"].apply(lambda x : difflib.get_close_matches(x, unique_spe_from_densite, n=1, cutoff = 0.6))

# Met la colonne sous forme de string et pas liste comme l'output du difflib
df_hono_global["spe_matched_cleaned"] = df_hono_global.spe_matched.apply(lambda x: np.nan if len(x)==0 else x[0])

# DRop la colonne spe_matched
df_hono_global.drop("spe_matched", axis=1, inplace = True)

# Check du travail de correspondance
df = df_hono_global[["specialite", "spe_matched_cleaned"]]

df2 = df[df.isnull().any(axis=1)]
df2["specialite"].unique().size

## Departement
# unique_dpt_from_densite = df_density_long["region"].unique()
#
# df_hono_global["dpt_matched"] = df_hono_global["department"].apply(lambda x : difflib.get_close_matches(x, unique_dpt_from_densite, n=1, cutoff = 0.6))
#
# df_hono_global["dpt_matched_cleaned"] = df_hono_global["dpt_matched"].apply(lambda x: np.nan if len(x)==0 else x[0])
#
# df_hono_global.drop("dpt_matched", axis=1, inplace = True)

df_density_long["dpt_number"] = df_density_long["region"].str.split(" ").str.get(0)
df_hono_global["dpt_number"] = df_hono_global["department"].str.split("-").str.get(0)

##########
###### TABLEAU DENSITE

## Specialisation

#  Ajout d'une colonne de correspondance a 60% sur le nom de la specialisation
# df_density_long["spe_matched"] = df_density_long["specialite"].apply(lambda x : difflib.get_close_matches(x, df_hono_global["specialite"], n=1, cutoff = 0.6))

# Met la colonne sous forme de string et pas liste comme l'output du difflib
# df_density_long["spe_matched_cleaned"] = df_density_long.spe_matched.apply(lambda x: np.nan if len(x)==0 else x[0])
# df_density_long.drop('spe_matched', axis=1, inplace = True)

## Departement
# df_density_long["dpt_matched"] = df_density_long["region"].apply(lambda x : difflib.get_close_matches(x, df_hono_global["department"], n=1, cutoff = 0.6))
#
# df_density_long["dpt_matched_cleaned"] = df_density_long["dpt_matched"].apply(lambda x: np.nan if len(x)==0 else x[0])
#
# df_density_long.drop("dpt_matched", axis=1, inplace = True)

##### Clean du data_honoraire global

## Creation de 2 DataFrame clean et concatenated

aggregation_functions = {'effectifs': 'sum', 'hono_sans_depass': 'sum', 'depass': 'sum', 'deplacement': 'sum',  'total_hono': 'sum'}
df_honoraire = df_hono_global.groupby(["dpt_number", "spe_matched_cleaned"]).aggregate(aggregation_functions)

###########
##### Mergin des 2 tableaux sur departement et spe
df_merged = pd.merge(df_density_long, df_hono_global, how='left', left_on=['specialite', 'dpt_number'], right_on=['spe_matched_cleaned', 'dpt_number'])

##### Create a cleaner dataFrame

df_merged.replace("nc", np.nan, inplace = True)
df_merged_nona = df_merged.dropna(axis=0, how="any", inplace=False)
df_cleaned = df_merged_nona[["region", "specialite_x", "type_", "effectifs", "hono_sans_depass", "depass", "deplacement", "total_hono"]]

############
### Analysis

# Renaming density column (# active operative per 100k' people)
df_cleaned["density"] = df_cleaned["type_"]
df_cleaned.drop("type_", inplace = True, axis=1)

# Calculating % of overcharge as percentage of total fees (excluding transport)

def overcharge_in_pct(row):
    total_fees = row["hono_sans_depass"] + row["depass"]
    if total_fees > 0:
        result = row["depass"] / (row["hono_sans_depass"] + row["depass"])
    else:
        result = np.nan
    return result


df_cleaned["overcharge_per_cent"] = df_cleaned.apply(overcharge_in_pct, axis=1)

df_cleaned.dropna(inplace = True)

df_cleaned.sort_values("region", inplace = True)

####################
## ANALYSE PAR DEPARTEMENT

df_analysis_by_dpt = df_cleaned.set_index("region")

result_by_dpt = pd.DataFrame(columns=["department", "corr_density_overcharge"])

for index, row in df_analysis_by_dpt.iterrows():
    print(index)
    print(result_by_dpt.head(1))
    print(index in result_by_dpt["department"])
    print("########")
    if index in result_by_dpt["department"].values:
        continue
    else:
        X_tmp = df_analysis_by_dpt.loc[index, "density"]
        y_tmp = df_analysis_by_dpt.loc[index, "overcharge_per_cent"]
        X_bis_tmp = X_tmp.values.reshape(-1, 1)
        ols_basic_tmp = LinearRegression().fit(X_bis_tmp, y_tmp)
        result_by_dpt = result_by_dpt.append({'department': index,
                        "corr_density_overcharge": ols_basic_tmp.score(X_bis_tmp, y_tmp)},
                       ignore_index=True)

result_by_dpt.sort_values("corr_density_overcharge", ascending = False, inplace=True)
####################

####################
## ANALYSE PAR SPECIALITE

df_analysis_by_spe = df_cleaned.set_index("specialite_x")

result_by_spe = pd.DataFrame(columns=["specialite", "corr_density_overcharge"])

for index, row in df_analysis_by_spe.iterrows():
    print(index)
    print(result_by_spe.head(1))
    print(index in result_by_spe["specialite"])
    print("########")
    if index in result_by_spe["specialite"].values:
        continue
    else:
        X_tmp = df_analysis_by_spe.loc[index, "density"]
        y_tmp = df_analysis_by_spe.loc[index, "overcharge_per_cent"]
        X_bis_tmp = X_tmp.values.reshape(-1, 1)
        ols_basic_tmp = LinearRegression().fit(X_bis_tmp, y_tmp)
        result_by_spe = result_by_spe.append({'specialite': index,
                        "corr_density_overcharge": ols_basic_tmp.score(X_bis_tmp, y_tmp)},
                       ignore_index=True)


result_by_spe.sort_values("corr_density_overcharge", ascending = False, inplace=True)


####################

effectif_by_dpt_by_age = pd.read_csv("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/RPPS/effectif_par_departement.csv", encoding='latin-1', skiprows=[0,1,2,3,5])
effectif_by_dpt_by_age.melt(id_vars = ["Unnamed: 0", "AGE"], value_vars = ["Ensemble tous âges confondus", "Moins de 30 ans", "Entre 30 et 34 ans", "Entre 35 et 39 ans", "Entre 40 et 44 ans", "Entre 45 et 49 ans", "Entre 50 et 54 ans", "Entre 55 et 59 ans", "Entre 60 et 64 ans", "Entre 65 et 69 ans", "70 ans et plus"])

effectif_by_dpt = effectif_by_dpt_by_age[["Unnamed: 0", "AGE", "Ensemble tous âges confondus"]]

effectif_columns = ["zone", "specialite", "effectif"]
effectif_by_dpt.columns = effectif_columns
effectif_by_dpt["dpt_number"] = effectif_by_dpt["zone"].str.split(" ").str.get(0)


####################

pop_insee_init = pd.read_excel("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/insee_pop.xls", sheet_name = 1, skiprows = 4)
pop_insee = pop_insee_init[pop_insee_init.columns[0:8].tolist()]

####################

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

df_dens_clean = df_dens_manual.drop(["0 à 19 ans", "20 à 39 ans", "40 à 59 ans", "60 à 74 ans", "75 ans et plus", "Total"], inplace=False, axis=1)

####################

# Revenus #

revenue_med_by_dpt = pd.read_excel("/home/theo/Documents/MASTER/Theo_Nazon/INFMDI721/Lesson_6/data/insee_rev.xls", sheet_name = "Données des cartes", skiprows=3)

columns_revenue = ["dpt_number", "dpt_name", "median_revenue", "D9/D1", "poverty_rate", "share_subsidied_revenue"]

revenue_med_by_dpt.columns = columns_revenue

####################

## Merging des tableaux de densite et de revenue

df_socio_demo = pd.merge(df_dens_clean, revenue_med_by_dpt, left_on="dpt_number", right_on="dpt_number")

## Merging des tableaux honoraires et socio demo

df_consolidated = pd.merge(df_honoraire, df_socio_demo, left_on)





