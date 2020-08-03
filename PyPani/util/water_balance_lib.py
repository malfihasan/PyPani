'''
__name__: PANI-py
__file_description__: This is the water balance module for PANI-py.  
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

# -- section : initial variable -- #
#  parameters for upward flow (Meyer Equation)-
PARAMA = 3.9
PARAMB = 3.8
PARAMC = 0.5


def water_balance_calculation( soil_sel, planting_sm, doy_pred, doy, pet_crop_pred,  ksp_new,  rain_mm, irrg_mm, \
       sel_yr_pred, water_table,  phase_i,   sm_file=None, v=False ):
    
    result_dict = dict()

    #   starting soil water conditions (at planting)-
    sw_surf = [0.0]                             # initial value of surface layer water, mm
    sw_deep = [(float(soil_sel.max_deep) * float(planting_sm))/100.0]     # initial value of deep profile water, mm
    deep_lost=[0.0]
    upflow = [0.0]
    t_phase_2 = 0.0                              # phase 2 time (days) initial value

    # Irrigation recommendation parameters--
    # stress_traget is the target stress level (0-1, 0 = no stress)
    # In this tool, stress_traget = 0 (no deficit irrigation)
    stress_traget = 0                                     #target stress level (0 = no stress)
    sw_tar_1_lower = 0.5*soil_sel.max_deep*(1.-stress_traget)   #lower SW target = critical SW for Type 1 stress
    sw_tar_2_lower = 0.3*soil_sel.max_deep*(1.-stress_traget)   #lower SW target = critical SW for Type 2 stress

    ephase1 = [0.0]
    ephase2 = [0.0]

    mat_day = 999    #indicator for crop maturity

    rain_pred = rain_mm + [0]*(len(doy_pred)-len(doy))
    irrg_pred = irrg_mm + [0]*(len(doy_pred)-len(doy))

    # print(len(rain_pred))
    # print(len(sumGDD))
    # print(len(pet_crop_pred))
    # print(sm_file)
    if sm_file != "NA":
        df_sm = pd.read_csv( sm_file )
        if(len(df_sm['sm_value']) < 1):
            print("No manual entry of soil moisture values are not provided.")

    cwu = [0.0]
    for k, doy_in in enumerate(doy_pred[:-1]):    # CAREFULL : THE STARTED HERE FROM one INSTEAD OF zero 
        i = k + 1
        cwu.append( pet_crop_pred[i] * ( ksp_new[i] / 100.0) ) 
        
        ## Soil Moisture calculation 
        if (sm_file != "NA"):
            if (len(df_sm['sm_value']) > 0):
                df_tmp = df_sm[(df_sm['jday']==doy_in) & (df_sm['year']==sel_yr_pred[i])]
                if (len(df_tmp['jday']) > 0 ):
                    sw_deep[(i-1)] = (list(df_sm['sm_value'])[0]*float(soil_sel.max_deep)) / 100.0
        
        ## Soil Water balance calculation 
        
        ### 'Calculate soil evaporation
        if sw_surf[(i-1)] > 0:
            etmp = pet_crop_pred[i] * ( 1 - ksp_new[i]/ 100.0)
            if etmp > sw_surf[(i-1)] :
                ephase1.append( sw_surf[(i-1)] ) 
                frac_phase = sw_surf[(i-1)] / etmp
                t_phase_2 = ( ( float(soil_sel.max_deep) - sw_deep[(i-1)] )/ float(soil_sel.alpha) )**2 + 1
                ephase2.append( ( (float(soil_sel.alpha)*math.sqrt(t_phase_2)) - ( float(soil_sel.alpha) * ( math.sqrt(t_phase_2) - 1.0)) )*(1.0 - frac_phase)  )
            else :
                ephase1.append( etmp ) 
                ephase2.append( 0.0 ) 
        else:
            if t_phase_2 == 0:
                t_phase_2 = (( float(soil_sel.max_deep) - sw_deep[(i-1)])/float(soil_sel.alpha))**2 + 1
            else:
                t_phase_2 =  t_phase_2 + 1 
            ephase1.append( 0.0 ) 
            ephase2.append(  (float(soil_sel.alpha)*math.sqrt(t_phase_2)) - ( float(soil_sel.alpha) * ( math.sqrt(t_phase_2) - 1.0)) ) 
        
        #print(i)
        sw_surf.append(sw_surf[(i-1)] - ephase1[i])
        sw_deepT = sw_deep[(i-1)] - ephase2[i] - cwu[i]
        if sw_deepT < 0 : sw_deepT = 0.0
        sw_deep.append(sw_deepT)
        
        # rainfall and irrigation 
        if (rain_pred[i] > 0.1)  or (irrg_pred[i] > 0.1):
            if rain_pred[i] > 0.1:
                if rain_pred[i] < (soil_sel.u - sw_surf[i]):
                    sw_surf[i] = sw_surf[i] + rain_pred[i]
                else:
                    sw_deep[i] = sw_deep[i] + rain_pred[i] - (soil_sel.u - sw_surf[i])
                    if sw_deep[i] > soil_sel.max_deep : 
                        deep_lost.append( sw_deep[i] -  soil_sel.max_deep )
                        sw_deep[i] = soil_sel.max_deep
                    sw_surf[i] = soil_sel.u
                    t_phase_2 = 0
            if irrg_pred[i] > 0.1:
                if irrg_pred[i] < (soil_sel.u - sw_surf[i]):
                    sw_surf[i] = sw_surf[i] + irrg_pred[i]
                else:
                    sw_deep[i] = sw_deep[i] + irrg_pred[i] - (soil_sel.u - sw_surf[i])
                    if sw_deep[i] > soil_sel.max_deep : 
                        deep_lost.append( sw_deep[i] -  soil_sel.max_deep )
                        sw_deep[i] = soil_sel.max_deep
                    sw_surf[i] = soil_sel.u
                    t_phase_2 = 0
            
        else:
            if v :
                print("No rain or irrigation")
            
        # calculate upward flow from water table
        if water_table == 1 : 
            if sw_deep[i] < soil_sel.max_deep:     # rooting zone not filled
                zx = ( soil_sel.surf_depth + soil_sel.deep_depth )/3000  # depth to 1/3 rooting zone (m)
                if water_table >= zx: 
                    zr = float(water_table) - zx 
                else:
                    zr = 0
                paramx = sw_deep[i]/soil_sel.max_deep

                # Meyer Equation for ratio of upward flow to ET-
                upratio = PARAMA / ( math.exp( PARAMB*zr/soil_sel.zmax )* (1 + math.exp(PARAMC/paramx + 0.01)) )
                upflow.append( upratio * (ephase1[i] + ephase2[i] + cwu[i])) # upward flow, mm
                sw_deep[i] = sw_deep[i] + upflow[i]
                if sw_deep[i] > soil_sel.max_deep : sw_deep[i] = soil_sel.max_deep

        #print(phase_i[i])

        # Crop has reached maturity- stop irrigation scheduling tool
        if phase_i[i] == 3 :
            mat_day = i
            print("The crop reached maturity at " + str(mat_day) + " days. Now terminating rest of calculation.")
            print("Date of Maturity: " + str(doy_pred[i]) + ", " + str(sel_year_pred[i]) )

            break

    result_dict['SW_SURF'] = sw_surf
    result_dict['SW_DEEP'] = sw_deep
    result_dict['DEEP_LOST'] = deep_lost
    result_dict['UPFLOW'] = upflow
    result_dict['PHASE_2'] = t_phase_2
    result_dict['EPHASE1'] = ephase1
    result_dict['EPHASE2'] = ephase2
    result_dict['CWU'] = cwu
    result_dict['RAIN_PRED'] = rain_pred
    result_dict['IRRG_PRED'] = irrg_pred
    result_dict['SW_TAR'] = { 'SW_tar_1': sw_tar_1_lower,
                              'SW_tar_2': sw_tar_2_lower }

    return result_dict
