'''
__name__: PANI-py
__file_description__: This is the weather module for PANI-py.  
__developer__ : M. Alfi Hasan
__developer_contact__: mdalfihasan19@gmail.com <malfihasan.com>
__python_version__: 3.5
__partner__: CIMMYT Bangladesh
__update_date__: 22 January, 2020
__version__: 1.01
'''

# -- section : library  -- #
import pandas as pd
import numpy as np
import os 
import sys
import json
from datetime import date, time, datetime
import math
import numpy as np

from PyPani.util.core_lib import *

##### %%%% Auxilary functions %%%% #####
def column_erro_msg(col_len, des_num):
     if col_len != des_num:
         print( "X"*10 + "..."*20 + "X"*10 )
         print( " Error in weather type selection OR wrong number of columns in the observed weather input file. Exiting...." )
         print( "X"*10 + "..."*20 + "X"*10 )
         sys.exit()


##### %%%% Observed weather data %%%% #####
# processing observed data

def obs_weather_pre_processing(obs_weather_file, weather_type, planting_year_in, planting_day_in, lat_in ):

    df_obs = pd.read_csv(obs_weather_file, header=None)

    # weather_type 
    ## type 1 : Penman-Monteith Method ( PMM)
    ## type 2 : Preistly-Taylor Method  (PTM)
    ## type 3 : Blainy-Criddle Method ( BCM)


    # defining the columns and rejecting any file that don't have that
    if weather_type == "PMM":
          column_erro_msg(len(df_obs.columns), 7)
          df_obs.columns = ['month', 'day', 'year', 'avg_temp', 'avg_dew', 'avg_wind', 'avg_solar']
    elif weather_type == "PTM":
          column_erro_msg(len(df_obs.columns), 6)
          df_obs.columns = ['month', 'day', 'year', 'max_temp', 'min_temp', 'avg_solar']  
    elif weather_type == "BCM":
          column_erro_msg(len(df_obs.columns), 5)
          df_obs.columns = ['month', 'day', 'year', 'max_temp', 'min_temp']    


    # solar_avg= []
    # solar_pct = []
    # dp_avec = []
    # wind_avg = []
    obs_result=dict()

    if (weather_type == "PMM") or (weather_type == "PTM"):
        
        # calculating and filtering doy and solar factors 
        obs_result['DOY'], obs_result['iStart'], obs_result['iEnd'], obs_result['DF_OBS'], obs_result['DAP'], obs_result['SEL_YR'], \
                obs_result['SLR_AVG'], obs_result['SLR_PCT'] = filter_only_plant_days(df_obs, planting_year_in, planting_day_in, lat_in, solar=True )

        # obs_result['DOY'] = doy
        # obs_result['iStart'] = i_start
        # obs_result['iEnd'] = i_end
        # obs_result['DF_OBS'] = df_obs
        # obs_result['DAP'] = dap
        # obs_result['SEL_YR'] = sel_yr
        # obs_result['SLR_AVG'] = solar_avg
        # obs_result['SLR_PCT'] = solar_pct

        if weather_type == "PMM":
            obs_result['TMP_AVG']= list(df_obs['avg_temp'])[obs_result['iStart']:obs_result['iEnd']]
            obs_result['DP_AVG']= list(df_obs['avg_dew'])[obs_result['iStart']:obs_result['iEnd']]
            obs_result['WIND_AVG'] = list(df_obs['avg_wind'])[obs_result['iStart']:obs_result['iEnd']]
        else: 
            obs_result['TMP_AVG'] = [ (i+j)/2 for i, j in zip(df_obs['max_temp'], df_obs['min_temp']) ][obs_result['iStart']:obs_result['iEnd']]
            obs_result['DP_AVG'] = list(df_obs['min_temp'])[obs_result['iStart']:obs_result['iEnd']]  
        
        # DEBUG SECTION #
        # print(len(tmp_avg))
        # print(len(dp_avec))
        # print(len(solar_pct))
        # print(solar_avg)
        #.  .#
        
            
    elif weather_type == "BCM":

        # calculating and filtering doy and solar factors 
        obs_result['DOY'], obs_result['iStart'], obs_result['iEnd'], obs_result['DF_OBS'], obs_result['DAP'], \
          obs_result['SEL_YR'] = filter_only_plant_days(df_obs, planting_year_in, planting_day_in, lat, solar=False )

        obs_result['TMP_AVG'] = [ (i+j)/2 for i, j in zip(df_obs['max_temp'], df_obs['min_temp']) ][obs_result['iStart']:obs_result['iEnd']]

    return(obs_result)


##### %%%% PET module %%%% #####
def pet_calculation(tmp_avg, elev, weather_type,  dp_avg=None, solar_avg=None, solar_pct=None, wind_avg=None, doy=None):
  '''
  A function to calculate PET based on different weather types
  '''
  
  # initializing variables for PET calculation 
  #print("TEST")
  rnet_crop = []
  rnet_soil = []
  pet_crop = []
  pet_soil = []
  result =dict()
  for i, val in enumerate(tmp_avg):
      if (weather_type == "PMM") or (weather_type == "PTM"):
          press = 101.3 * (((293.0 - 0.0065*float(elev))/293.0)**5.26) # atmospheric pressure (kPa), FAO-56 Eq. 7
          heatvap = 2.45  # Latent heat of vaporization (MJ/kg), FAO-56 p. 26
          satvp = 0.6108*math.exp(17.27*(tmp_avg[i] /(tmp_avg[i]+237.3))) 
          vp = 0.6108*math.exp(17.27*(dp_avg[i] /(dp_avg[i]+237.3)))  # FAO-56 Eq. 14\
          vpd = satvp - vp
          # Slope of the saturation vapor pressure curve (delta, kPa/deg C, FAO-56 Eq. 13)--
          delta = ( 4098.0*0.6108 * math.exp(17.27*(tmp_avg[i] /(tmp_avg[i]+237.3))) )/( (tmp_avg[i]+237.3)*(tmp_avg[i]+237.3) )
          # Psychrometric constant (gamma, kPa/deg C, FAO-56 Eq. 8)--
          gamma = 0.665*press /1000.0
          cp = 1.013 /1000.0  # specific heat of air at const pressure (MJ /kg /deg C)
          r = 0.287  # Universal Gas Constant (kJ /kg /deg K)
          rho = press /(r *(tmp_avg[i]+273.)) # air density (kg/m3) from Universal Gas Law
          
          # For crops 
          albedo = 0.23    # shortwave albedo of crops (FAO-56 p. 51, and Chang Table 1)
          rns = solar_avg[i]*(1.- albedo) # net daily shortwave radiation (MJ/m2, FAO-56 Eq. 38)
          tmp_avg_k = tmp_avg[i] + 273. # convert deg C -> deg K
          sigma = 4.903 /1.0e9  # Stefan-Boltzmann constant (MJ /deg K4 /m2 /day)
          # Net outgoing longwave radiation (MJ/m2, FAO-56 Eq. 39)--
          rnl = sigma * ( tmp_avg_k ** 4) * (0.34 -0.14*math.sqrt(vp)) * (1.35*solar_pct[i]/100.0 - 0.35)
          rnet_crop.append( rns - rnl ) # Net radiation for crop (MJ/m2), FAO-56 Eq. 40
          
          # For soil--
          albedo = 0.15 # shortwave albedo of soil
          rns = solar_avg[i]*(1.- albedo) # net daily shortwave radiation (MJ/m2, FAO-56 Eq. 38)
          rnet_soil.append( rns - rnl )# Net radiation for soil (MJ/m2), FAO-56 Eq. 40
          g = 0.0 # Soil heat flux, daily value assumed zero (FAO-56 Eq. 42)
          
          if weather_type == "PMM":
              
              ## Penman-Monteith Equation-
              
              # For crop--
              windht = 2. # Equivalent height (m) above crop wind would be measured
              zo = 0.04 # Roughness length (m), crop canopy
              vonk = 0.41 # Von Karman constant, FAO-56 p. 20
              
              # Aerodynamic resistance (RA, s/m, FAO-56 Eq. 4):
              racrop = ( math.log((windht)/zo)*math.log((windht)/zo) ) /(vonk*vonk*wind_avg[i])
              
              # For soil--
              zo = 0.0045 # Roughness length (m), bare soil
              rasoil = ( math.log((windht)/zo)*math.log((windht)/zo) ) /(vonk*vonk*wind_avg[i])
              rs = 50.0 # Surface resistance for well-watered crop or wet soil (s/m)
              
              # For crop--
              term1 = delta *(rnet_crop[i]- g )
              term2 = rho*cp*vpd /racrop
              denom = delta  + gamma*(1.+rs/racrop)
              
              # Latent heat flux (MJ/m2), Penman-Monteith Equation, FAO-56 Eq. 3:
              heatlt = (term1 +term2*SECDAY) /denom
              pet_crop.append( heatlt /heatvap ) # PET for crop (kg/m2/day = mm/day)
              
              # For soil--
              term1 = delta *(rnet_soil[i]- g )
              term2 = rho*cp*vpd /rasoil
              denom = delta  + gamma*(1.+rs/rasoil)
              
              # Latent heat flux (MJ/m2), Penman-Monteith Equation, FAO-56 Eq. 3:
              heatlt = (term1 +term2*SECDAY) /denom
              pet_soil.append( heatlt /heatvap )# PET for soil (kg/m2/day = mm/day)

          else :
              
              ## Priestly-Taylor Equation-
              
              # For crop--
              temp1 = 1.336*delta*(rnet_crop[i]-g)
              term2 = 0.0
              denom = delta + gamma
              
              # Latent heat flux (MJ/m2), Priestly-Taylor Equation-
              heatlt = (temp1 + (term2*SECDAY)) /denom
              pet_crop.append ( heatlt /heatvap ) # PET for crop (kg/m2/day = mm/day)
              
              # For soil--
              temp1 = 1.336*delta*(rnet_soil[i]-g)
              term2 = 0.
              denom = delta + gamma
              
              # Latent heat flux (MJ/m2), Priestly-Taylor Equation-
              heatlt = (temp1 + term2*SECDAY) /denom
              pet_soil.append ( heatlt /heatvap ) # PET for soil (kg/m2/day = mm/day)
              
      elif weather_type == "BCM":
          # Blainy-Criddle Equation-
          sunfac = 0.014*(math.sin(6.28*doy[i]/365. + 4.71)) + 0.084
          tmp_avg_f = (tmp_avg[i]*1.8) + 32.
          bccwu = 0.850*( tmp_avg_f * sunfac * (25.4 /30.5) )
          pet_crop.append(bccwu)
          pet_soil.append(bccwu)

  result['PET_CROP'] = pet_crop 
  result['PET_SOIL'] = pet_soil 

  if (weather_type == "PMM") or (weather_type == "PTM"):
        result['RNET_CROP'] = rnet_crop
        result['RNET_SOIL'] = rnet_soil

  return result


##### %%%% Forcast weather data %%%% #####

def forecast_weather_data( pred_weather_file, main_result, current_DAP, planting_year_in, planting_day_in):

  # forecast data
  df_pred = pd.read_csv(pred_weather_file, header=None)
  df_pred.columns = ['month', 'day', 'year', 'max_temp', 'min_temp']

  df_pred['date'] = [ date(int(x), int(y), int(z)) for x, y, z in zip(df_pred['year'], df_pred['month'], df_pred['day']) ]
  df_pred['jday'] = [ x.timetuple().tm_yday for x in df_pred['date'] ]


  # << ___ fix for extra observed data __ >> 
  dap = [ i for i in main_result['DAP'] if i <= current_DAP]
  doy_pred = main_result['DOY'][0:len(dap)]
  sel_yr_pred = main_result['SEL_YR'][0:len(dap)]
  tmp_avg_pred = main_result['TMP_AVG'][0:len(dap)]
  pet_crop_pred = main_result['PET_CROP'][0:len(dap)]
  pet_soil_pred = main_result['PET_SOIL'][0:len(dap)]

  
  obs_len = len(doy_pred) - 1 

  for i_n, [jd, yr] in enumerate(zip( df_pred['jday'] , df_pred['year'] )):
      dfp_wrk = find_day_after_planting( planting_year_in, planting_day_in, yr, jd)
      if (dfp_wrk is not None) and (dfp_wrk > current_DAP ) :
          #print(str(df_pred['date'][i_n]) + "  : " +  str(dfp_wrk) + ",  " + str(jd))
          if (dfp_wrk < (current_DAP+8)):
              doy_pred.append(jd)
              sel_yr_pred.append(yr)
              tmp_avg_pred.append( (list(df_pred['max_temp'])[i_n] + list(df_pred['min_temp'])[i_n])/2 ) 
              obs_len = obs_len + 1 
              sunfac = 0.014*(math.sin(6.28*doy_pred[(obs_len) ]/365. + 4.71)) + 0.084
              tmp_avg_f = (tmp_avg_pred[(obs_len)]*1.8) + 32.
              bccwu = 0.850*( tmp_avg_f * sunfac * (25.4 /30.5) )
              pet_crop_pred.append(bccwu)
              pet_soil_pred.append(bccwu)


  main_result['DOY_PRED'] = doy_pred
  main_result['SEL_YR_PRED'] = sel_yr_pred
  main_result['TMP_AVG_PRED'] = tmp_avg_pred
  main_result['PET_CROP_PRED'] = pet_crop_pred
  main_result['PET_SOIL_PRED'] = pet_soil_pred

  return main_result