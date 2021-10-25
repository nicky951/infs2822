from flask import Flask
import pandas as pd
import pandasql as ps

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == '__main__':

    # ra - maps postcode to remoteness classifications (city, regional, rural)
    # ras - maps each postcode to a single classification based on the classification that makes up majority of the postcode
    ra = pd.read_excel('CG_POSTCODE_2017_RA_2016.xls', sheet_name='Table 3', header=5, skipfooter=4, converters={'POSTCODE_2017':str})
    ras = ps.sqldf("SELECT POSTCODE_2017, RA_NAME_2016, MAX(RATIO) FROM ra GROUP BY POSTCODE_2017;")
    ras['POSTCODE_2017'] = 'POA' + ras['POSTCODE_2017']

    # g01/g02 - Overall postcode stats like income and population
    g01 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G01_AUS_POA.csv')
    g02 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G02_AUS_POA.csv')

    # g47 - field of study
    g47a = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47A_AUS_POA.csv')
    g47b = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47B_AUS_POA.csv')
    g47c = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G47C_AUS_POA.csv')
    g47 = pd.concat([g47a, g47b, g47c, g01, g02], axis=1, sort=False)

    # g16 year 12 completion
    g16a = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16A_AUS_POA.csv')
    g16b = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G16B_AUS_POA.csv')
    g16 = pd.concat([g16a, g16b], axis=1, sort=False)

    # g15 type of education institution
    g15 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G15_AUS_POA.csv')

    # g07 indigenous australian identifiers
    g07 = pd.read_csv('2016_GCP_POA_for_AUS_short-header/2016 Census GCP Postal Areas for AUST/2016Census_G07_AUS_POA.csv')
    
    # make a table of relevant statistics for all australian postcodes
    all_stats = ps.sqldf('''SELECT 
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
        FROM g47 a LEFT JOIN ras b ON a.POA_CODE_2016 == b.POSTCODE_2017 
        LEFT JOIN g01 c ON a.Poa_code_2016 == c.POA_CODE_2016 
        LEFT JOIN g02 d ON a.POA_CODE_2016 == d.POA_CODE_2016 
        LEFT JOIN g15 e ON a.POA_CODE_2016 == e.POA_CODE_2016 
        LEFT JOIN g16 f ON a.POA_CODE_2016 == f.POA_CODE_2016 
        LEFT JOIN g07 g ON a.POA_CODE_2016 == g.POA_CODE_2016 
        WHERE b.RA_NAME_2016 NOT IN ('Major Cities of Australia') 
        AND c.Tot_P_P > 5000;''')

    # export this table to csv so that it can be used by our web-based map app
    all_stats.to_csv("web/static/postcode-stats.csv", index=False)

    # getting min/max of statistics for the map's colour helper
    Tot_P_P_bounds = ["Tot_P_P",all_stats["Tot_P_P"].median(), all_stats["Tot_P_P"].min(), all_stats["Tot_P_P"].max() ]
    STEM_Pct_bounds = ["STEM_Pct", all_stats["STEM_Pct"].median(), all_stats["STEM_Pct"].min(), all_stats["STEM_Pct"].max()]
    Wkly_Hhd_Inc_bounds = ["Wkly_Hhd_Inc", all_stats["Wkly_Hhd_Inc"].median(), all_stats["Wkly_Hhd_Inc"].min(), all_stats["Wkly_Hhd_Inc"].max()]
    Y12_Comp_Pct_bounds = ["Y12_Comp_Pct", all_stats["Y12_Comp_Pct"].median(), all_stats["Y12_Comp_Pct"].min(), all_stats["Y12_Comp_Pct"].max()]
    Secondary_Tot_P_bounds = ["Secondary_Tot_P", all_stats["Secondary_Tot_P"].median(), all_stats["Secondary_Tot_P"].min(), all_stats["Secondary_Tot_P"].max()]
    Secondary_Pct_bounds = ["Secondary_Pct", all_stats["Secondary_Pct"].median(), all_stats["Secondary_Pct"].min(), all_stats["Secondary_Pct"].max()]
    Tec_Furt_Educ_inst_Tot_P_bounds = ["Tec_Furt_Educ_inst_Tot_P", all_stats["Tec_Furt_Educ_inst_Tot_P"].median(), all_stats["Tec_Furt_Educ_inst_Tot_P"].min(), all_stats["Tec_Furt_Educ_inst_Tot_P"].max()]
    TAFE_Pct_bounds = ["TAFE_Pct", all_stats["TAFE_Pct"].median(), all_stats["TAFE_Pct"].min(), all_stats["TAFE_Pct"].max()]
    Uni_other_Tert_Instit_Tot_P_bounds = ["Uni_other_Tert_Instit_Tot_P", all_stats["Uni_other_Tert_Instit_Tot_P"].median(), all_stats["Uni_other_Tert_Instit_Tot_P"].min(), all_stats["Uni_other_Tert_Instit_Tot_P"].max()]
    Uni_Pct_bounds = ["Uni_Pct", all_stats["Uni_Pct"].median(), all_stats["Uni_Pct"].min(), all_stats["Uni_Pct"].max()]
    Indigenous_Pct_bounds = ["Indigenous_Pct", all_stats["Indigenous_Pct"].median(), all_stats["Indigenous_Pct"].min(), all_stats["Indigenous_Pct"].max()]
    
    colour_bounds = [Tot_P_P_bounds, STEM_Pct_bounds, Wkly_Hhd_Inc_bounds, Y12_Comp_Pct_bounds, Secondary_Tot_P_bounds
        , Secondary_Pct_bounds, Tec_Furt_Educ_inst_Tot_P_bounds, TAFE_Pct_bounds, Uni_other_Tert_Instit_Tot_P_bounds, Uni_Pct_bounds, Indigenous_Pct_bounds]

    stats_min_max = pd.DataFrame(colour_bounds,columns=['stat','median','min','max'])
    stats_min_max.to_csv("web/static/stats-min-max.csv", index=False)

    del ra, ras
    del g01, g02
    del g15
    del g16a, g16b, g16
    del g47, g47a, g47b, g47c
    del Tot_P_P_bounds, STEM_Pct_bounds, Wkly_Hhd_Inc_bounds, Y12_Comp_Pct_bounds, Secondary_Tot_P_bounds, Secondary_Pct_bounds, Tec_Furt_Educ_inst_Tot_P_bounds, TAFE_Pct_bounds, Uni_other_Tert_Instit_Tot_P_bounds, Uni_Pct_bounds, Indigenous_Pct_bounds
    del colour_bounds, stats_min_max

    app.run()
