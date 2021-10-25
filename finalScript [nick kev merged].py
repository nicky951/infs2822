import numpy as np
import pandas as pd
import pandasql as psql
import seaborn as sns
import matplotlib.pyplot as plt

divider = "-------------------------------------------------------------------------------------------------------------------------------------------------------------"

# Get table for mapping postcodes to how remote they are
ra = pd.read_excel('CG_POSTCODE_2017_RA_2016.xls', sheet_name='Table 3', header=5, skipfooter=4, converters={'POSTCODE_2017':str})
ras = psql.sqldf("SELECT POSTCODE_2017, RA_NAME_2016, MAX(RATIO) FROM ra GROUP BY POSTCODE_2017;")
ras['POSTCODE_2017'] = 'POA' + ras['POSTCODE_2017']

# Get average median income statistics of major city Autralia
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')
g02 = psql.sqldf('''SELECT * FROM g02 a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    WHERE b.RA_NAME_2016 IN ('Major Cities of Australia') 
    AND a.Median_tot_hhd_inc_weekly <> 0;''')
print(divider)
print("\nMedian city incomes: \n")
print(g02.median(axis =0))

# Get average median income of regional (non major city) Australia
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')
g02 = psql.sqldf('''SELECT * FROM g02 a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
    AND a.Median_tot_hhd_inc_weekly <> 0;''')
print(divider)
print("\nMedian rural incomes: \n")
print(g02.median(axis=0))

del(g02)

# g47 - Non-school qualification by age by sex
df_2016A = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47A_AUS_POA.csv')
df_2016B = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47B_AUS_POA.csv')
df_2016C = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47C_AUS_POA.csv')

 # g01/g02 - Overall postcode stats like income and population
g01 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G01_AUS_POA.csv')
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')

# Cleaned and combined df
df_2016Merged = pd.concat([df_2016A, df_2016B, df_2016C, g01, g02], axis=1, sort=False)

# Cleaned CSV of POA and remoteness classification
remote = pd.read_csv('CG_POSTCODE_2017_RA_2016.csv')

# Query appends the remoteness classification to the postcode in dataset
queryJoinRemotePostcode = psql.sqldf("SELECT remote.RA_NAME_2016, MAX(remote.RATIO) AS Ratio, df_2016Merged.POA_CODE_2016,"
+ " df_2016Merged.P_NatPhyl_Scn_Tot, df_2016Merged.P_InfoTech_Tot, df_2016Merged.P_Eng_RelTec_Tot, df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot,"
+ " df_2016Merged.P_NatPhyl_Scn_Tot + df_2016Merged.P_InfoTech_Tot + df_2016Merged.P_Eng_RelTec_Tot + df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot AS 'Total_STEM'," 
+ " df_2016Merged.Tot_P_P AS 'Total_Population',"
+ " ((df_2016Merged.P_NatPhyl_Scn_Tot + df_2016Merged.P_InfoTech_Tot + df_2016Merged.P_Eng_RelTec_Tot + df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot * 1.0)"
+ " /df_2016Merged.P_Tot_Tot  * 1.0) AS 'Percent'"
+ " FROM df_2016Merged INNER JOIN remote ON df_2016Merged.POA_CODE_2016 = remote.POSTCODE_2017" 
+ " WHERE RA_NAME_2016 NOT LIKE '%Major Cities of Australia%'"
+ " AND df_2016Merged.Tot_P_P > 5000"
+ " GROUP BY remote.POSTCODE_2017")

queryOrderDesc = psql.sqldf("SELECT * FROM queryJoinRemotePostcode WHERE Ratio > 0.5 ORDER BY Percent ASC LIMIT 15")

print(divider)
print("\nTotal Percentage of STEM Fields of Study per Postcode:\n")
print(queryOrderDesc)

# g16 - Year of highschool completed per postcode
df_2016G16A = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16A_AUS_POA.csv')
df_2016G16B = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16B_AUS_POA.csv')

g16 = pd.concat([df_2016G16A, df_2016G16B], axis=1, sort=False)

# Save memory
del df_2016A
del df_2016B
del df_2016C
del df_2016G16A
del df_2016G16B

# Subquery with POA for highschool completion
queryHighschoolByPostcode = psql.sqldf("SELECT POA_CODE_2016, P_Y12e_Tot, P_Y11e_Tot, P_Y10e_Tot, P_Y9e_Tot, P_Y8b_Tot, P_DNGTS_Tot, P_Tot_Tot," 
+ " ((P_Y12e_Tot * 1.0) / (P_Tot_Tot * 1.0)) AS 'Percent Year 12 Completion'"
+ " FROM g16 WHERE POA_CODE_2016 IN"
+ " (SELECT POA_CODE_2016 FROM queryOrderDesc)"
+ " ORDER BY P_Y12e_Tot DESC")

print(divider)
print("\nPercentage of Year 12 Completion Rate to Population per Postcode:\n")
print(queryHighschoolByPostcode)

# Query for the top 10 low income postal areas
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')
g02 = psql.sqldf('''SELECT * FROM g02 a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
    AND a.Median_tot_hhd_inc_weekly <> 0;''')

g02df = g02.nsmallest(10, ['Median_tot_hhd_inc_weekly'])[['POA_CODE_2016','Median_tot_hhd_inc_weekly']]

print(divider)
print("\nLowest Non-City Weekly Household Income Postcodes:\n")
print(g02df)

# g15 - Proportion of population undertaking studies
g01 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G01_AUS_POA.csv')
g15 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G15_AUS_POA.csv')
g15['Total_Pop'] = g01['Tot_P_P']
g15 = psql.sqldf('''SELECT * FROM g15 a INNER JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
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

# df for largest proportion of population in Secondary Education
g15sedf = g15.nlargest(10, ['Pct_In_Secondary'])[['POA_CODE_2016','Secondary_Tot_P','Total_Pop','Pct_In_Secondary']]

# df for largest proportion of population in Technical Further Education
g15tfedf = g15.nlargest(10, ['Pct_In_TFEI'])[['POA_CODE_2016','Tec_Furt_Educ_inst_Tot_P','Total_Pop','Pct_In_TFEI']]

# df for largest proportion of population in University
g15lpudf = g15.nsmallest(10, ['Pct_In_Uni'])[['POA_CODE_2016','Uni_other_Tert_Instit_Tot_P','Total_Pop','Pct_In_Uni']]

print(divider)
print("\nPostcodes with largest proportion of population in Secondary Education:\n")
print(g15sedf)

print(divider)
print("\nPostcodes with largest proportion of population in Technical Further Education:\n")
print(g15tfedf)

print(divider)
print("\nPostcodes with lowest proportion of population in Uni:\n")
print(g15lpudf)

# g51 - Industry of employment by age and sex
g51 = pd.read_csv("2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G51A_AUS_POA.csv")
g51b = pd.read_csv("2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G51B_AUS_POA.csv")
g51c = pd.read_csv("2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G51C_AUS_POA.csv")
g51d = pd.read_csv("2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G51D_AUS_POA.csv")

# Combine into a single df
g51df = pd.concat([g51, g51b, g51c, g51d], axis=1, sort=False)

# Query on selected 3 postcodes. Based off analysis of previous results earlier in script
postcodes = psql.sqldf("SELECT * FROM g51df WHERE POA_CODE_2016 in ('POA2820', 'POA3450', 'POA3280')")
total_stem_table = pd.DataFrame(data=postcodes)

# Query for all industries for women
total_female_jobs = psql.sqldf("SELECT POA_CODE_2016, F_Ag_For_Fshg_Tot, F_Mining_Tot, F_Manufact_Tot, F_El_Gas_Wt_Waste_Tot, F_Constru_Tot, F_WhlesaleTde_Tot, F_RetTde_Tot,"
+ " F_Accom_food_Tot, F_Trans_post_wrehsg_Tot, F_Info_media_teleco_Tot, F_Fin_Insur_Tot, F_RtnHir_REst_Tot, F_Pro_scien_tec_Tot, F_Admin_supp_Tot,"
+ " F_Public_admin_sfty_Tot, F_Educ_trng_Tot, F_HlthCare_SocAs_Tot, F_Art_recn_Tot, F_Oth_scs_Tot, F_ID_NS_Tot FROM total_stem_table")
total_female_jobs_table = pd.DataFrame(data=total_female_jobs)

total_female_jobs_table["Total_number_of_female_workers"] = total_female_jobs_table.sum(axis=1)

# Query for STEM related industries for women
total_female_stem_jobs = psql.sqldf("SELECT POA_CODE_2016, F_Ag_For_Fshg_Tot, F_Pro_scien_tec_Tot, F_Info_media_teleco_Tot FROM total_female_jobs_table")
total_female_stem_jobs_table = pd.DataFrame(data=total_female_stem_jobs)
total_female_stem_jobs_table["Total number of female stem jobs"] = total_female_stem_jobs_table.sum(axis=1)
alist = total_female_stem_jobs_table["Total number of female stem jobs"].tolist()

total_female_jobs_table["Total_number_of_female_stem_jobs"] = alist
arrpct = []
for i in range(0, 3):
    work = total_female_jobs_table.iloc[i][-1]
    total = total_female_jobs_table.iloc[i][-2]
    pct = work/total
    formatpct = (round(pct, 4) * 100)
    arrpct.append(formatpct)

total_female_jobs_table["percentage_of_female_stem"] = arrpct
finalFemale = psql.sqldf("SELECT POA_CODE_2016, Total_number_of_female_stem_jobs, Total_number_of_female_workers, percentage_of_female_stem FROM total_female_jobs_table"
+ " ORDER BY percentage_of_female_stem")

print(divider)
print("\nNumber and Percentage of Females in STEM related jobs:\n")
print(finalFemale)

# Query for all industries for men
total_male_jobs = psql.sqldf("SELECT POA_CODE_2016, M_Ag_For_Fshg_Tot, M_Mining_Tot, M_Manufact_Tot, M_El_Gas_Wt_Waste_Tot, M_Constru_Tot, M_WhlesaleTde_Tot, M_RetTde_Tot,"
+ " M_Accom_food_Tot, M_Trans_post_wrehsg_Tot, M_Info_media_teleco_Tot, M_Fin_Insur_Tot, M_RtnHir_REst_Tot, M_Pro_scien_tec_Tot, M_Admin_supp_Tot,"
+ " M_Public_admin_sfty_Tot, M_Educ_trng_Tot, M_HlthCare_SocAs_Tot, M_Art_recn_Tot, M_Oth_scs_Tot, M_ID_NS_Tot FROM total_stem_table")
total_male_jobs_table = pd.DataFrame(data=total_male_jobs)

total_male_jobs_table["Total_number_of_male_workers"] = total_male_jobs_table.sum(axis=1)

# Query for STEM related industries for men
total_male_stem_jobs = psql.sqldf("SELECT POA_CODE_2016, M_Ag_For_Fshg_Tot, M_Pro_scien_tec_Tot, M_Info_media_teleco_Tot FROM total_male_jobs_table")
total_male_stem_jobs_table = pd.DataFrame(data=total_male_stem_jobs)
total_male_stem_jobs_table["Total number of male stem jobs"] = total_male_stem_jobs_table.sum(axis=1)
alist = total_male_stem_jobs_table["Total number of male stem jobs"].tolist()

total_male_jobs_table["Total_number_of_male_stem_jobs"] = alist
arrpct = []
for i in range(0, 3):
    male_work = total_male_jobs_table.iloc[i][-1]
    male_total = total_male_jobs_table.iloc[i][-2]
    pct = male_work/male_total
    formatpct = (round(pct, 4) * 100)
    arrpct.append(formatpct)

total_male_jobs_table["percentage_of_male_stem"] = arrpct
finalMale = psql.sqldf("SELECT POA_CODE_2016, Total_number_of_male_stem_jobs, Total_number_of_male_workers, percentage_of_male_stem FROM total_male_jobs_table ORDER BY percentage_of_male_stem")

print(divider)
print("\nNumber and Percentage of Males in STEM related jobs:\n")
print(finalMale)

# g07 indigenous australian identifiers
g07 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G07_AUS_POA.csv')

# Collated Statistics Table
all_stats = psql.sqldf('''SELECT 
    a.POA_CODE_2016
    , b.RA_NAME_2016
    , c.Tot_P_P
    , (a.P_NatPhyl_Scn_Tot + a.P_InfoTech_Tot + a.P_Eng_RelTec_Tot + a.P_Ag_Envir_Rltd_Sts_Tot) AS STEM_Tot
    , a.P_Tot_Tot
    , (((a.P_NatPhyl_Scn_Tot + a.P_InfoTech_Tot + a.P_Eng_RelTec_Tot + a.P_Ag_Envir_Rltd_Sts_Tot)*100.0) / (a.P_Tot_Tot*1.0)) AS STEM_Pct
    , d.Median_tot_hhd_inc_weekly AS Wkly_Hhd_Inc
    , e.Secondary_Tot_P
    , ((e.Secondary_Tot_P*100.0) / (c.Tot_P_P*1.0)) AS Secondary_Pct
    , e.Tec_Furt_Educ_inst_Tot_P
    , ((e.Tec_Furt_Educ_inst_Tot_P*100.0) / (c.Tot_P_P*1.0)) AS TAFE_Pct
    , e.Uni_other_Tert_Instit_Tot_P
    , ((e.Uni_other_Tert_Instit_Tot_P*100.0) / (c.Tot_P_P*1.0)) AS Uni_Pct
    , ((f.P_Y12e_Tot * 100.0) / (f.P_Tot_Tot * 1.0)) AS Y12_Comp_Pct
    , ((g.Tot_Indigenous_P * 100.0) / (c.Tot_P_P*1.0)) AS Indigenous_Pct 
    FROM df_2016Merged a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
    LEFT JOIN g01 c ON a.Poa_code_2016 == c.POA_CODE_2016 
    LEFT JOIN g02 d ON a.POA_CODE_2016 == d.POA_CODE_2016 
    LEFT JOIN g15 e ON a.POA_CODE_2016 == e.POA_CODE_2016 
    LEFT JOIN g16 f ON a.POA_CODE_2016 == f.POA_CODE_2016 
    LEFT JOIN g07 g ON a.POA_CODE_2016 == g.POA_CODE_2016 
    WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
    AND c.Tot_P_P > 5000;''')

all_stats.to_csv("postcode-stats.csv", index=False)
print(divider)
print("\nAll Statistics:\n")
print(all_stats)

# Graphical Representation of data

# Code to set color palette for high values
# Credits and Source: https://stackoverflow.com/questions/36271302/changing-color-scale-in-seaborn-bar-plot
def colors_from_values(values, palette_name):
    # normalize the values to range [0, 1]
    normalized = (values - min(values)) / (max(values) - min(values))
    # convert to indices
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
    # use the indices to get the colors
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)


#Barplots of above datasets
totalStemPlot = sns.barplot(data=queryOrderDesc,x='POA_CODE_2016', y='Percent', palette = colors_from_values(queryOrderDesc['Percent'], "OrRd"))
totalStemPlot.set(xlabel='POA Code', ylabel='Percent STEM Field of Study')
totalStemPlot.set_title("Lowest 15 Postal Areas in STEM Field of Study")
totalStemPlot.figure.set_size_inches(13,5)
totalStemPlot.figure.savefig('graphs/totalStemPlot.png')

plt.clf()

highschoolCompletionPlot = sns.barplot(data=queryHighschoolByPostcode,x='POA_CODE_2016', y='Percent Year 12 Completion', palette = colors_from_values(queryHighschoolByPostcode['Percent Year 12 Completion'], "RdYlGn"))
highschoolCompletionPlot.set(xlabel='POA Code', ylabel='Percent Year 12 Completion')
highschoolCompletionPlot.set_title("Percentage of Year 12 Completion per Postal Area")
highschoolCompletionPlot.figure.set_size_inches(13,5)
highschoolCompletionPlot.figure.savefig('graphs/highschoolCompletionPlot.png')


plt.clf()

pctFemalePlot = sns.barplot(data=finalFemale,x='POA_CODE_2016', y='percentage_of_female_stem')
pctFemalePlot.set(xlabel='POA Code', ylabel='Percent of Female Working Population in STEM Jobs')
pctFemalePlot.set_title("Percentage of Female STEM Jobs per Postal Area")
pctFemalePlot.figure.set_size_inches(13,5)
pctFemalePlot.figure.savefig('graphs/pctFemalePlot.png')

plt.clf()

pctMalePlot = sns.barplot(data=finalMale,x='POA_CODE_2016', y='percentage_of_male_stem')
pctMalePlot.set(xlabel='POA Code', ylabel='Percent of Male Working Population in STEM Jobs')
pctMalePlot.set_title("Percentage of Male STEM Jobs per Postal Area")
pctMalePlot.figure.set_size_inches(13,5)
pctMalePlot.figure.savefig('graphs/pctMalePlot.png')

plt.clf()

medianIncomePlot = sns.barplot(data=g02df,x='POA_CODE_2016', y='Median_tot_hhd_inc_weekly', palette = colors_from_values(g02df['Median_tot_hhd_inc_weekly'], "RdYlGn"))
medianIncomePlot.set(xlabel='POA Code', ylabel='Median Total Household Income (Weekly)')
medianIncomePlot.set_title("Lowest Non-City Weekly Household Income per Postal Area")
medianIncomePlot.figure.set_size_inches(13,5)
medianIncomePlot.figure.savefig('graphs/medianIncomePlot.png')

plt.clf()

populationTFEPlot = sns.barplot(data=g15tfedf,x='POA_CODE_2016', y='Pct_In_TFEI', palette = colors_from_values(g15tfedf['Pct_In_TFEI'], "RdYlGn"))
populationTFEPlot.set(xlabel='POA Code', ylabel='Percent of Population in Technical Further Education')
populationTFEPlot.set_title("Percentage of Population in Technical Further Education per Postal Area")
populationTFEPlot.figure.set_size_inches(13,5)
populationTFEPlot.figure.savefig('graphs/populationTFEPlot.png')

plt.clf()

populationUniPlot = sns.barplot(data=g15lpudf,x='POA_CODE_2016', y='Pct_In_Uni', palette = colors_from_values(g15lpudf['Pct_In_Uni'], "RdYlGn"))
populationUniPlot.set(xlabel='POA Code', ylabel='Percent of Population in University')
populationUniPlot.set_title("Percentage of Population in University per Postal Area")
populationUniPlot.figure.set_size_inches(13,5)
populationUniPlot.figure.savefig('graphs/populationUniPlot.png')

plt.clf()

populationSecEdPlot = sns.barplot(data=g15sedf,x='POA_CODE_2016', y='Pct_In_Secondary', palette = colors_from_values(g15sedf['Pct_In_Secondary'], "RdYlGn"))
populationSecEdPlot.set(xlabel='POA Code', ylabel='Percent of Population in Secondary Education')
populationSecEdPlot.set_title("Percentage of Population in Secondary Education per Postal Area")
populationSecEdPlot.figure.set_size_inches(13,5)
populationSecEdPlot.figure.savefig('graphs/populationSecEdPlot.png')
