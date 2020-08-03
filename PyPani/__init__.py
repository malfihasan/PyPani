'''
__name__: PANI-py
__objective__: To give irrigation recommendation before one week to the stakeholders.  
__developer__ : M. Alfi Hasan
__developer_contact__: mdalfihasan19@gmail.com <malfihasan.com>
__python_version__: 3.5
__partner__: CIMMYT Bangladesh
__update_date__: 27 January, 2020
__version__: 1.01
'''

'''

DESCRIPTION
-------------

Required Input:

1. Historical observed daily weather data ( Minimum requirement: Daily maximum and minimum temperature, 
                                            Solar radiation )
2. Seven-day forcasted daily weather data ( Minimum requirement: Daily maximum and minimum temperature )
3. Soil profile information ( There are 10 type of soil profile provided with the package)
4. Rainfall data ( rainfall information for the desired crop season. The data needs to be available, from
                   sowing date of that perticular season )
5. Corp infomation.

Output : 

1. Irrigation recommendation after 7 days.
2. Calculated metrixes for entire selected season.

'''

# -- section : Python libraries  -- #
import pandas as pd
import numpy as np
import os 
import json
from datetime import date, time, datetime
import math
import numpy as np

# -- section : User libraries  -- #
import PyPani.config as main_cfg
from PyPani.util.core_lib import *
from PyPani.util.weather_lib import *
from PyPani.util.env_lib import *
from PyPani.util.water_balance_lib import *
from PyPani.util.recommend import *

def recommendation_engine( dayI, monthI, yearI, planting_jdayI, planting_yearI):
    cfg = main_cfg.UAF_config(dayI, monthI, yearI, planting_jdayI, planting_yearI)
    month = cfg.month # Month value for current date
    day = cfg.day # Day value for current date 
    current_year = cfg.year # Year value for current date
    current_date_obj = date(current_year, month, day) # converting to a date object for further use
    current_jday = current_date_obj.timetuple().tm_yday  

    planting_day = cfg.planting_jday
    planting_year = cfg.planting_year

    id_txt = cfg.id_txt # User defined process/field name 
    lat =  float(cfg.lat) # Lattitude [ default latitude for Barishal, Bangladesh ]
    elev = float(cfg.elev) # Elevation [ default elevation for Barishal, Bangladesh ]

    obs_weather_file = cfg.obs_weather_file # Observed weather file
    pred_weather_file = cfg.pred_weather_file # Predicted/Forecasted weather file
    weather_type = cfg.pet_cal_method # PET calculation method.

    crop_type = cfg.crop # Crop type 

    ksp_file = cfg.ksp_file # KSP coefficient/ Ground cover file 
    rainfall_file = cfg.rainfall_file # Rainfall file
    irrg_file = cfg.irrg_file # Irrigation file
    sm_file = cfg.sm_file  # Soil moisture file
    max_irrg =  cfg.max_irrg # Maximum allowable irrigation [ values are in mm ] 
    soil_type =  cfg.soil_type # Soil type
    planting_sm =  cfg.planting_sm # Soil moisture at planting [ values are in percentage ]
    water_table =  cfg.water_table # Water table NA or any depth at (m)[ values are in mm ]
    out_file =  cfg.outfile # Outputfile required?
    recom =  cfg.recom # Recommendation file name

    # print everything
    def print_config():
        print("----- The processing begins : the inputs are as follow ----")
        print("***** Input config file *****")
        print(" current date as julian days and year : " + str(current_jday) + ", " + str(current_year) )
        print(" planting date as julian days and year : " + str(planting_day) + ", " + str(planting_year) )
        print(" given lattitude : " + str(lat) )
        print(" given elevation : " + str(elev) )
        print(" PET calculation method : " + str(weather_type) )
        print(" weather files : " + str(obs_weather_file) + ", " + str(pred_weather_file) )
        print(" ground cover curve number file : " + str(ksp_file) )
        print(" rainfall file : " + str(rainfall_file) )
        print(" irrigation file : " + str(irrg_file) )
        print(" soil moisture file : " + str(sm_file) )
        print(" maximum irrigation given during planting : " + str(max_irrg) )
        print(" soil moisture at planting : " + str(planting_sm) )
        print(" water table depth : " + str(water_table) )
        print(" output file : " + str(out_file) )
        print("----------------------------")
        print("Config sucessfully imported!")
        print("     ")

    print_config()

    ## --> determining days after planting for leap year correction
    current_DAP = find_day_after_planting( planting_year, planting_day, current_year, current_jday, msg=True)

    ##### %%%% Observed weather data %%%% #####
    obs_result = obs_weather_pre_processing(obs_weather_file, weather_type, planting_year,
                                       planting_day, lat)

    ##### %%%% PET module %%%% #####
    if weather_type == "PMM": 
        PET_result = pet_calculation(obs_result['TMP_AVG'],elev, weather_type,
                                     dp_avg= obs_result['DP_AVG'], solar_avg= obs_result['SLR_AVG'],
                                    solar_pct= obs_result['SLR_PCT'], wind_avg=obs_result['WIND_AVG']) 
    elif weather_type == "PTM": 
        PET_result = pet_calculation(obs_result['TMP_AVG'],elev, weather_type,
                                     dp_avg= obs_result['DP_AVG'], solar_avg= obs_result['SLR_AVG'],
                                    solar_pct= obs_result['SLR_PCT']) 
    elif weather_type == "BCM": 
        PET_result = pet_calculation(obs_result['TMP_AVG'],elev, weather_type, doy=obs_result['DOY'])

    obs_result.update(PET_result)

    ##### %%%% Forecast module %%%% #####
    core_dict = forecast_weather_data( pred_weather_file, obs_result.copy(), 
                                    current_DAP, planting_year, planting_day)

    
    ##### %%%% GC module %%%% #####
    crop_i = main_cfg.crop_growth(crop_type)
    crop_base = crop_i.base

    gd_dict = GDD_calculation(core_dict['DOY_PRED'], core_dict['TMP_AVG_PRED'], crop_base, crop_i)

    core_dict.update(gd_dict.copy())

    if ksp_file != "NA":
        ksp_dict = update_observed_GC( ksp_file, core_dict['DOY_PRED'], core_dict['KSP'] )

        core_dict.update(ksp_dict.copy())


    ##### %%%% Env. module %%%% #####
    rain_dict = update_observed_rainfall( rainfall_file, core_dict['DOY'], core_dict['SEL_YR'] )
    core_dict.update(rain_dict.copy() )

    if irrg_file != "NA":
        irrg_dict = update_observed_irrigation( irrg_file, core_dict['DOY'], core_dict['SEL_YR'] )
        core_dict.update(irrg_dict.copy() )

    if sm_file != "NA":
        sm_dict = update_observed_sm( sm_file)
        core_dict.update(sm_dict.copy() )

    
    ##### %%%% Water Balance module %%%% #####
    soil_sel = main_cfg.soil_profile(soil_type)

    water_dict = water_balance_calculation( soil_sel, 
                              planting_sm, 
                              core_dict['DOY_PRED'], core_dict['DOY'],
                              core_dict['PET_CROP_PRED'],  
                              core_dict['KSP_NEW'],  core_dict['RAIN'], 
                              core_dict['IRRG'], core_dict['SEL_YR_PRED'], 
                              water_table,  core_dict['PHASE_I'],   
                              sm_file=sm_file )
    core_dict.update(water_dict)


    
    if out_file != "NA":
        write_output(out_file, core_dict)
    
    if recom !="NA":
        recommendation( len(core_dict['DOY']), len(core_dict['DOY_PRED']), len(core_dict['DAP']), max_irrg,  core_dict, soil_sel, outName=cfg.recom)


