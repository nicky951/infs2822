import pandas as pd
import pandasql as ps
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


g01 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G01_AUS_POA.csv')

# get table for mapping postcodes to how remote they are
ra = pd.read_excel('CG_POSTCODE_2017_RA_2016.xls', sheet_name='Table 3', header=5, skipfooter=4, converters={'POSTCODE_2017':str})
ras = ps.sqldf("SELECT POSTCODE_2017, RA_NAME_2016, MAX(RATIO) FROM ra GROUP BY POSTCODE_2017;")
ras['POSTCODE_2017'] = 'POA' + ras['POSTCODE_2017']


# G47 TABLE - FIELD OF STUDY
g47a = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47A_AUS_POA.csv')
g47b = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47B_AUS_POA.csv')
g47c = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47C_AUS_POA.csv')

g47 = ps.sqldf('''SELECT * FROM g47a a INNER JOIN g47b b ON a.POA_CODE_2016 == b.POA_CODE_2016 
    INNER JOIN g47c c ON a.POA_CODE_2016 == c.POA_CODE_2016
    INNER JOIN g01 e ON a.POA_CODE_2016 == e.POA_CODE_2016
    LEFT JOIN ras d ON a.POA_CODE_2016 == d.POSTCODE_2017 
    WHERE d.RA_NAME_2016 NOT IN ('Major Cities of Australia')
    AND c.P_Tot_Tot > 5000;''')

def stem_study_total (row):
    return row['P_NatPhyl_Scn_Tot'] + row['P_InfoTech_Tot'] + row['P_Eng_RelTec_Tot'] + row['P_ArchtBldng_Tot'] + row['P_Ag_Envir_Rltd_Sts_Tot'] + row['P_Health_Tot']

g47['STEM_Tot'] = g47.apply (lambda row: stem_study_total(row), axis=1)

def stem_study_pct (row):
    if (row['P_Tot_Tot'] == 0):
        return float('NaN')
    else:
        return row['STEM_Tot'] / row['P_Tot_Tot'] * 100

g47['STEM_Pct'] = g47.apply (lambda row:stem_study_pct(row), axis=1)


print('Postcodes with smallest percentage of STEM studies')
low_stem = ps.sqldf("SELECT POA_CODE_2016, RA_NAME_2016, STEM_Tot, P_Tot_Tot, STEM_Pct FROM g47").nsmallest(15, ['STEM_Pct'])
print(low_stem)

del g47


# TOP 10 LOW INCOME POSTCODES
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')
g02_sub = ps.sqldf('''SELECT * FROM g02 a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
    AND a.Median_tot_hhd_inc_weekly <> 0;''')

g02df = g02.nsmallest(10, ['Median_tot_hhd_inc_weekly'])[['POA_CODE_2016','Median_tot_hhd_inc_weekly']]
print("Lowest non-city weekly household income postcodes")
<<<<<<< HEAD:kevin.py
print(g02_sub.nsmallest(15, ['Median_tot_hhd_inc_weekly'])[['POA_CODE_2016','Median_tot_hhd_inc_weekly']])
=======
print(g02df)
>>>>>>> master:draft_scripts/kevin.py

# income of our top 10 lowest stem suburbs
low_stem_income = ps.sqldf("SELECT a.POA_CODE_2016, STEM_Tot, P_Tot_Tot, STEM_Pct, Median_tot_hhd_inc_weekly FROM low_stem a LEFT JOIN g02_sub b ON a.POA_CODE_2016 == b.POA_CODE_2016;")
print(low_stem_income)

# stats of our top 10 lowest stem suburbs
low_stem_income2 = ps.sqldf("SELECT a.POA_CODE_2016, Median_age_persons AS Med_age, Median_mortgage_repay_monthly AS Med_mthly_mortgage, Median_tot_prsnl_inc_weekly AS Med_prsn_inc, Median_rent_weekly, Median_tot_fam_inc_weekly AS Med_fam_inc, Median_tot_hhd_inc_weekly AS Med_hhd_inc, Average_household_size AS Avg_hhd_size FROM low_stem a LEFT JOIN g02_sub b ON a.POA_CODE_2016 == b.POA_CODE_2016;")
print(low_stem_income2)

# median city income vs regional/remote income
median_city_inc = ps.sqldf("SELECT POA_CODE_2016, Median_tot_hhd_inc_weekly FROM g02 a JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 WHERE RA_NAME_2016 = 'Major Cities of Australia';")
print('Median income for city postcodes: ' +  str(median_city_inc['Median_tot_hhd_inc_weekly'].median()))

median_noncity_inc = ps.sqldf("SELECT POA_CODE_2016, Median_tot_hhd_inc_weekly FROM g02 a JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 WHERE RA_NAME_2016 NOT IN ('Major Cities of Australia');")
print('Median income for regional/remote postcodes: ' + str(median_noncity_inc['Median_tot_hhd_inc_weekly'].median()))

# G15 TABLE - where students are studying
g15 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G15_AUS_POA.csv')
g15['Total_Pop'] = g01['Tot_P_P']
g15 = ps.sqldf('''SELECT * FROM g15 a INNER JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    JOIN low_stem c ON a.POA_CODE_2016 == c.POA_CODE_2016
    WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
    AND a.Total_Pop > 5000;''')

def pct_in_secondary (row):
    if (row['Total_Pop'] == 0):
        return float('NaN')
    else:
        return row['Secondary_Tot_P']/row['Total_Pop'] * 100

def pct_in_tfei (row):
    if (row['Total_Pop'] == 0):
        return float('NaN')
    else:
        return row['Tec_Furt_Educ_inst_Tot_P']/row['Total_Pop'] * 100

def pct_in_uni (row):
    if (row['Total_Pop'] == 0):
        return float('NaN')
    else:
        return row['Uni_other_Tert_Instit_Tot_P']/row['Total_Pop'] * 100

g15['Pct_In_Secondary'] = g15.apply (lambda row: pct_in_secondary(row), axis=1)
g15['Pct_In_TFEI'] = g15.apply (lambda row: pct_in_tfei(row), axis=1)
g15['Pct_In_Uni'] = g15.apply (lambda row: pct_in_uni(row), axis=1)

<<<<<<< HEAD:kevin.py
# print(g15[['POA_CODE_2016','Total_Pop','Secondary_Tot_P','Pct_In_Secondary','Tec_Furt_Educ_inst_Tot_P','Pct_In_TFEI','Uni_other_Tert_Instit_Tot_P','Pct_In_Uni']])
print(g15[['POA_CODE_2016','Total_Pop','Pct_In_Secondary','Pct_In_TFEI','Pct_In_Uni']])

# print("Postcodes with largest proportion of population in secondary education")
# print(g15.nlargest(10, ['Pct_In_Secondary'])[['POA_CODE_2016','Secondary_Tot_P','Total_Pop','Pct_In_Secondary']])

# print("Postcodes with largest proportion of population in Technical Further Education")
# print(g15.nlargest(10, ['Pct_In_TFEI'])[['POA_CODE_2016','Tec_Furt_Educ_inst_Tot_P','Total_Pop','Pct_In_TFEI']])

# print("Postcodes with lowest proportion of population in Uni")
# print(g15.nsmallest(10, ['Pct_In_Uni'])[['POA_CODE_2016','Uni_other_Tert_Instit_Tot_P','Total_Pop','Pct_In_Uni']])
=======
#df for largest proportion of population in secondary education
g15sedf = g15.nlargest(10, ['Pct_In_Secondary'])[['POA_CODE_2016','Secondary_Tot_P','Total_Pop','Pct_In_Secondary']]
g15tfedf = g15.nlargest(10, ['Pct_In_TFEI'])[['POA_CODE_2016','Tec_Furt_Educ_inst_Tot_P','Total_Pop','Pct_In_TFEI']]
g15lpudf = g15.nsmallest(10, ['Pct_In_Uni'])[['POA_CODE_2016','Uni_other_Tert_Instit_Tot_P','Total_Pop','Pct_In_Uni']]
print("Postcodes with largest proportion of population in secondary education")
print(g15sedf)

print("Postcodes with largest proportion of population in Technical Further Education")
print(g15tfedf)

print("Postcodes with lowest proportion of population in Uni")
print(g15lpudf)


# G47 TABLE - FIELD OF STUDY
g47a = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47A_AUS_POA.csv')
g47b = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47B_AUS_POA.csv')
g47c = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47C_AUS_POA.csv')

g47 = ps.sqldf('''SELECT * FROM g47a a INNER JOIN g47b b ON a.POA_CODE_2016 == b.POA_CODE_2016 
    INNER JOIN g47c c ON a.POA_CODE_2016 == c.POA_CODE_2016
    INNER JOIN g01 e ON a.POA_CODE_2016 == e.POA_CODE_2016
    LEFT JOIN ras d ON a.POA_CODE_2016 == d.POSTCODE_2017 
    WHERE d.RA_NAME_2016 NOT IN ('Major Cities of Australia')
    AND c.P_Tot_Tot > 5000;''')

def stem_study_total (row):
    return row['P_NatPhyl_Scn_Tot'] + row['P_InfoTech_Tot'] + row['P_Eng_RelTec_Tot'] + row['P_ArchtBldng_Tot'] + row['P_Ag_Envir_Rltd_Sts_Tot'] + row['P_Health_Tot']

g47['STEM_Tot'] = g47.apply (lambda row: stem_study_total(row), axis=1)

def stem_study_pct (row):
    if (row['P_Tot_Tot'] == 0):
        return float('NaN')
    else:
        return row['STEM_Tot'] / row['P_Tot_Tot'] * 100

g47['STEM_Pct'] = g47.apply (lambda row:stem_study_pct(row), axis=1)


print('Postcodes with smallest percentage of STEM studies')
print(ps.sqldf("SELECT POA_CODE_2016, RA_NAME_2016, STEM_Tot, P_Tot_Tot, STEM_Pct FROM g47").nsmallest(10, ['STEM_Pct']))
print(ps.sqldf("SELECT P_NatPhyl_Scn_Tot, P_InfoTech_Tot, P_Eng_RelTec_Tot, P_ArchtBldng_Tot, P_Ag_Envir_Rltd_Sts_Tot, P_Health_Tot, STEM_Tot, P_Tot_Tot, STEM_Pct FROM g47").nsmallest(10,['STEM_Pct']))

#Code to set color palette for high values
#Source:https://stackoverflow.com/questions/36271302/changing-color-scale-in-seaborn-bar-plot
def colors_from_values(values, palette_name):
    # normalize the values to range [0, 1]
    normalized = (values - min(values)) / (max(values) - min(values))
    # convert to indices
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
    # use the indices to get the colors
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)

plt.figure(figsize=(13,4))
sns.barplot(data=g15sedf,x='POA_CODE_2016', y='Pct_In_Secondary', palette = colors_from_values(g15sedf['Pct_In_Secondary'], "RdYlGn"))
plt.tight_layout()
plt.show()

plt.figure(figsize=(13,4))
sns.barplot(data=g02df,x='POA_CODE_2016', y='Median_tot_hhd_inc_weekly', palette = colors_from_values(g02df['Median_tot_hhd_inc_weekly'], "RdYlGn"))
plt.tight_layout()
plt.show()

plt.figure(figsize=(13,4))
sns.barplot(data=g15tfedf,x='POA_CODE_2016', y='Pct_In_TFEI', palette = colors_from_values(g15tfedf['Pct_In_TFEI'], "RdYlGn"))
plt.tight_layout()
plt.show()

plt.figure(figsize=(13,4))
sns.barplot(data=g15lpudf,x='POA_CODE_2016', y='Pct_In_Uni', palette = colors_from_values(g15lpudf['Pct_In_Uni'], "RdYlGn"))
plt.tight_layout()
plt.show()


>>>>>>> master:draft_scripts/kevin.py
