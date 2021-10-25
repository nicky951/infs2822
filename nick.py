import numpy as np
import pandas as pd
import pandasql as psql
import seaborn as sns
import matplotlib.pyplot as plt

#Read 2016 CSV data
# df_2016A = pd.read_csv('/Users/nicholasliang/Desktop/INFS2822group/2016_GCP_POA_for_NSW_short-header/2016 Census GCP Postal Areas for NSW/2016Census_G47A_NSW_POA.csv')
# df_2016B = pd.read_csv('/Users/nicholasliang/Desktop/INFS2822group/2016_GCP_POA_for_NSW_short-header/2016 Census GCP Postal Areas for NSW/2016Census_G47B_NSW_POA.csv')
# df_2016C = pd.read_csv('/Users/nicholasliang/Desktop/INFS2822group/2016_GCP_POA_for_NSW_short-header/2016 Census GCP Postal Areas for NSW/2016Census_G47C_NSW_POA.csv')

df_2016A = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47A_AUS_POA.csv')
df_2016B = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47B_AUS_POA.csv')
df_2016C = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47C_AUS_POA.csv')

 # g01/g02 - Overall postcode stats like income and population
g01 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G01_AUS_POA.csv')
g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')


#Cleaned 
df_2016Merged = pd.concat([df_2016A, df_2016B, df_2016C, g01, g02], axis=1, sort=False)

#Cleaned CSV of POA and remoteness classification
remote = pd.read_csv('remoteClassification.csv')

#Query appends the remoteness classification to the postcode in dataset
queryJoinRemotePostcode = psql.sqldf("SELECT remote.RA_NAME_2016, MAX(remote.RATIO) AS Ratio, df_2016Merged.POA_CODE_2016, df_2016Merged.P_NatPhyl_Scn_Tot, df_2016Merged.P_InfoTech_Tot, df_2016Merged.P_Eng_RelTec_Tot, "
+ "  df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot,"
+ " df_2016Merged.P_NatPhyl_Scn_Tot + df_2016Merged.P_InfoTech_Tot + df_2016Merged.P_Eng_RelTec_Tot + df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot AS 'Total_STEM'," 
+ " df_2016Merged.Tot_P_P AS 'Total_Population',"
+ " ((df_2016Merged.P_NatPhyl_Scn_Tot + df_2016Merged.P_InfoTech_Tot + df_2016Merged.P_Eng_RelTec_Tot + df_2016Merged.P_Ag_Envir_Rltd_Sts_Tot * 1.0)"
+ " /df_2016Merged.P_Tot_Tot  * 1.0) AS 'Percent'"
+ " FROM df_2016Merged INNER JOIN remote ON df_2016Merged.POA_CODE_2016 = remote.POSTCODE_2017" 
+ " WHERE RA_NAME_2016 NOT LIKE '%Major Cities of Australia%'"
+ " AND df_2016Merged.Tot_P_P > 5000"
+ " GROUP BY remote.POSTCODE_2017")

queryOrderDesc = psql.sqldf("SELECT * FROM queryJoinRemotePostcode WHERE Ratio > 0.5 ORDER BY Percent ASC LIMIT 15")

df_2016G16A = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16A_AUS_POA.csv')
df_2016G16B = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16B_AUS_POA.csv')

df_2016G16Merged = pd.concat([df_2016G16A, df_2016G16B], axis=1, sort=False)

#Save memory
del df_2016A
del df_2016B
del df_2016C
del df_2016G16A
del df_2016G16B

print(queryOrderDesc)

#Subquery with POA
queryHighschoolByPostcode = psql.sqldf("SELECT POA_CODE_2016, P_Y12e_Tot, P_Y11e_Tot, P_Y10e_Tot, P_Y9e_Tot, P_Y8b_Tot, P_DNGTS_Tot, P_Tot_Tot, ((P_Y12e_Tot * 1.0) / (P_Tot_Tot * 1.0)) AS 'Percent Year 12 Completion'"
+ " FROM df_2016G16Merged WHERE POA_CODE_2016 IN"
+ " (SELECT POA_CODE_2016 FROM queryOrderDesc)"
+ " ORDER BY P_Y12e_Tot DESC")

print(queryHighschoolByPostcode)

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

#Plot highschool completion in barchart
plt.figure(figsize=(13,4))
sns.barplot(data=queryHighschoolByPostcode,x='POA_CODE_2016', y='Percent Year 12 Completion', palette = colors_from_values(queryHighschoolByPostcode['Percent Year 12 Completion'], "RdYlGn"))
plt.tight_layout()
plt.show()
