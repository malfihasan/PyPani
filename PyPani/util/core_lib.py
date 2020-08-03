'''
__name__: PANI-py
__file_description__: This is the core module for PANI-py.  
__developer__ : M. Alfi Hasan
__developer_contact__: mdalfihasan19@gmail.com <malfihasan.com>
__python_version__: 3.5
__partner__: CIMMYT Bangladesh
__update_date__: 11 January, 2020
__version__: 1.01
'''

# -- section : library  -- #
import pandas as pd
import numpy as np
import os 
import json
from datetime import date, time, datetime
import math
import numpy as np
from collections import OrderedDict

# -- section : initial variable -- #
month_days = [0,31,59,90,120,151,181,212,243,273,304,334]
PI = 3.14159
LSNOON = 13  # hour of local solar moon (approx)
SOLCON = 1360  # solar constant, W/m2
SECDAY = 86400  # Number of seconds in a day


def print_summary_dict(dict_in):
    print("# of elements: ", len(dict_in.keys()) )
    print("Name of the keys: ", dict_in.keys())


    # count of the keys 
    for k, v in dict_in.items():
        if isinstance(v, list):
            print("-> Item [", k, "] is a list, data type for the first element is", str(type(v[0])).split('\'')[1], "and total number of elements :", len(v))
            print("---> First element and last element of [",k,"] :",v[0], ",", v[-1] )

        elif isinstance(v, dict):
            print("-> Item [", k, "] is a dictionary, it has total", len(v.keys()), "items. " )
        else:
            if str(type(v)).split('\'')[1] == "pandas.core.frame.DataFrame" : 
                print("-> Item [", k, "] is a", str(type(v)).split('\'')[1], "type object.  " )
            else:
                print("-> Item [", k, "] is a", str(type(v)).split('\'')[1], "type object. The value is ", v )



def find_day_after_planting( plant_year, plant_day, year_in, day_in, msg=False) :
    DAP_out = None
    if int(year_in) == int(plant_year) :
        if int(day_in) > int(plant_day):
            DAP_out = int(day_in) - int(plant_day)
        else:
            if msg:
                print("Current date is before planting date in same year!!!")
    elif int(year_in) > int(plant_year) : 
        if ( int(plant_year) % 4 == 0 ) and (int(plant_year) % 100 != 0 ) :
            DAP_out = int(day_in) + ( 366 - int(plant_day))
        else:
            DAP_out = int(day_in) + ( 365 - int(plant_day))
    else:
        if msg:
            print("Planning date later than current dates! Sorry, this program can not calculate future planting scenarios!!!!")
    return DAP_out

def solar_calculation(jday_in, lat_in):
    sumsolar = 0 
    for ih in range(1,24):
        decline = (math.sin(jday_in+100)*(2*PI/365))*((-23.5)*PI)/180
        alatrad = lat_in * (PI/180)
        hourang = (ih - LSNOON)*(2.0*PI)/24
        cossza = (math.sin(alatrad)*math.sin(decline)) + (math.cos(alatrad)*math.cos(decline)*math.cos(hourang))
        sza = PI/2.0 - math.atan(cossza/math.sqrt(1.0 - cossza*cossza))
        szadeg = sza * 180.0 / PI
        solmax = SOLCON*math.cos(sza)
        if solmax > 0 :
            sumsolar = sumsolar + solmax*3600.0/(1.0e6)
        #print(ih)
    return sumsolar 

def filter_only_plant_days(df_obs_in, planting_year_in, planting_day_in, lat_in, solar=False ):

    df_obs_in['date'] = [ date(int(x), int(y), int(z)) for x, y, z in zip(df_obs_in['year'], df_obs_in['month'], df_obs_in['day']) ]
    df_obs_in['jday'] = [ x.timetuple().tm_yday for x in df_obs_in['date'] ]
    #current_jday = current_date_obj.timetuple().tm_yday # 1st : CurrentDate$ value specified 
    doy = []
    sel_yr = []
    solar_day = []
    daf = []
    i_start = -1    
    for i_n, [jd, yr] in enumerate(zip( df_obs_in['jday'] , df_obs_in['year'] )):
        dfp_wrk = find_day_after_planting( planting_year_in, planting_day_in, yr, jd)
        #print(str(df_obs_in['date'][i_n]) + "  : " +  str(dfp_wrk) + ",  " + str(jd))
        if dfp_wrk is not None:
            if i_start < 0:
                i_start = i_n
            i_end = i_n+1
            doy.append(jd)
            sel_yr.append(yr)
            daf.append(dfp_wrk)
            if solar:
                sumsolar = solar_calculation(jd, lat_in)
                solar_day.append(sumsolar)
    
    if solar:
        solar_avg = list(df_obs_in['avg_solar'])[i_start:i_end]
        solar_pct = [(100.0 * i )/ ( j *0.7) for i, j in zip(solar_avg, solar_day)]
        solar_pct = [ 100.0 if i > 100 else i for i in solar_pct]
        return(doy, i_start, i_end, df_obs_in, daf, sel_yr, solar_avg, solar_pct)
    else:
        return(doy, i_start, i_end, df_obs_in, daf, sel_yr)


def write_output(out_file, dict_in):
    if 'SLR_AVG' in dict_in:
        solar_avg=dict_in['SLR_AVG']+ [0]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
        solar_pct=dict_in['SLR_PCT'] + [0]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
        
        if 'DP_AVG' in dict_in:
            dp_avg = dict_in['DP_AVG'] + [0]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
        else:  
            dp_avg = [None]*len(dict_in['DOY_PRED'])
        
        if 'WIND_AVG' in dict_in:
            wind_avg = dict_in['WIND_AVG'] + [0]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
        else:
            wind_avg = [None]*len(dict_in['DOY_PRED'])

    else:
        solar_avg= [None]*len(dict_in['DOY_PRED'])
        solar_pct = [None]*len(dict_in['DOY_PRED'])
        dp_avg = [None]*len(dict_in['DOY_PRED'])
        wind_avg = [None]*len(dict_in['DOY_PRED'])

    rnet_soil_pred = dict_in['RNET_SOIL'] +  [None]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
    rnet_crop_pred = dict_in['RNET_CROP'] +  [None]*(len(dict_in['DOY_PRED'])-len(dict_in['DOY']))
  
    df_out = pd.DataFrame( {"Julian_Day": dict_in['DOY_PRED'], 
                            "Year":dict_in['SEL_YR_PRED'], 
                            "Average_Temperature": dict_in['TMP_AVG_PRED'],
                            "PET_Soil": dict_in['PET_SOIL_PRED'],
                            "PET_Crop" : dict_in['PET_CROP_PRED'],
                            "Crop_Water_Use_CWU" : dict_in['CWU'],
                            "KSP_values": dict_in['KSP_NEW'],
                            "GDD": dict_in['SUM_GDD'],
                            "Phase of the crop": dict_in['PHASE_I'],
                            "Surface_water_depth": dict_in['SW_SURF'],
                            "Deep_water_depth": dict_in['SW_DEEP'],
#                             "Deep water lose": deep_lost,
                            "Ephase_1": dict_in['EPHASE1'],
                            "Ephase_2": dict_in['EPHASE2'],
                            "Rainfall": dict_in['RAIN_PRED'],
                            "Irrigation": dict_in['IRRG_PRED'],
                            "Solar_Avg":solar_avg,
                            "Solar_Percent":solar_pct,
                            "Wind_Avg":wind_avg,
                            "Dew_Point_Temperature":dp_avg,
                            "Res. Soil": rnet_soil_pred,
                            "Res. Crop" : rnet_crop_pred,
                            
                           } )
    df_out['Total_ET'] = df_out['Ephase_1'] + df_out['Ephase_2'] + df_out['Crop_Water_Use_CWU']
    df_out['Soil_Evap.'] = df_out['Ephase_1'] + df_out['Ephase_2']
    
    df_out.to_csv(out_file, index=False)

