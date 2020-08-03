'''
__name__: PANI-py
__file_description__: This is the recommend module for PANI-py.  
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


  
##### %%%% Recommend Function  %%%% #####

def recommendation( doy_len, doy_pred_len, dap_len, max_irrg, dict_in, soil_sel, outName="recommend_v2.txt"):

    ephase1 = dict_in['EPHASE1']
    ephase2 = dict_in['EPHASE2']
    cwu = dict_in['CWU']
    sw_deep = dict_in['SW_DEEP']
    phase_i = dict_in['PHASE_I']

    sw_xtra = soil_sel.u               # extra amount of irrigation that must be applied to account for soil evaporation
    irr_trigger = 0            # irrigation trigger = 0 (no irrigation needed), = 1 (irrigation needed)
    n_day_stress = 0           # number of days in the next 7 days with water stress
    cum_evap = 0.0             # used to accumulate ET over the predicted week
    sw_tar_1_lower = dict_in['SW_TAR']['SW_tar_1']
    sw_tar_2_lower = dict_in['SW_TAR']['SW_tar_2']

    forecast_day = doy_pred_len - doy_len
    for i in range(doy_len, doy_pred_len):
        cum_evap = cum_evap + ephase1[i] + ephase2[i] + cwu[i]
        if phase_i[i] == 1 : 
            # vegetative phase, Type 1 stress
            if sw_deep[i] <= sw_tar_1_lower:
                irr_trigger = 1
                n_day_stress = n_day_stress + 1 
                fill_prof = soil_sel.max_deep - sw_deep[i] + sw_xtra
                mini_irrig = sw_tar_1_lower - sw_deep[i] +sw_xtra
                add_irrig = mini_irrig + cum_evap*3 
                if add_irrig > max_irrg : add_irrig = max_irrg
                if add_irrig > fill_prof : add_irrig = fill_prof
        else:
            if sw_deep[i] <= sw_tar_2_lower: 
                irr_trigger = 1
                n_day_stress = n_day_stress + 1 
                fill_prof = soil_sel.max_deep - sw_deep[i] + sw_xtra
                mini_irrig = sw_tar_2_lower - sw_deep[i] +sw_xtra
                add_irrig = mini_irrig + cum_evap*3 
                if add_irrig > max_irrg : add_irrig = max_irrg
                if add_irrig > fill_prof : add_irrig = fill_prof


    current_pos = (dap_len-1)

    outF = open(outName, "w")


    pofc = 100* sw_deep[current_pos]/soil_sel.max_deep
    pof_cmm = sw_deep[current_pos]
    outF.write("Percent of Field Capacity  = "  + str(pofc) + "  (" + str(pof_cmm) + " mm)\n")

    if phase_i[current_pos] <= 1 :
        pasl = 100*( sw_deep[current_pos] - sw_tar_1_lower) / (soil_sel.max_deep - sw_tar_1_lower) 
        paslmm = sw_deep[current_pos] - sw_tar_1_lower
    else :
        pasl = 100*( sw_deep[current_pos] - sw_tar_2_lower) / (soil_sel.max_deep - sw_tar_2_lower) 
        paslmm = sw_deep[current_pos] - sw_tar_2_lower

    if pasl >= 0 :
        outF.write("Percent Above Stress Level = "  + str(pasl) + "  (" + str(paslmm) + " mm)\n")
    else:
        outF.write("Warning! ")
        outF.write("Percent Below Stress Level = "  + str(pasl) + "  (" + str(paslmm) + " mm)\n") 




    if irr_trigger == 1:
        if n_day_stress >= 7 :
            outF.write("\n********* IRRIGATION ALERT ********* \n")
            outF.write("The field needs to be irrigated as soon as possible.\n")
            if add_irrig == fill_prof :
                outF.write("Irrig. Recom. (mm): " + str(add_irrig) + "\n")
            else :
                outF.write("Irrig. Recom. (mm): " + str(add_irrig) + " to " + str(fill_prof)+ "\n")
            outF.write("To fill soil profile (mm): " + str(fill_prof)+ "\n")
        else :
            # field will reach stress during the coming week
            outF.write("\n********* IRRIGATION ALERT *********\n")
            outF.write("The field needs to be irrigated in next 7 days !"+ "\n")
            if add_irrig == fill_prof :
                outF.write("Irrig. Recom. (mm): " + str(add_irrig)+ "\n")
            else :
                outF.write("Irrig. Recom. (mm): " + str(add_irrig) + " to " + str(fill_prof)+ "\n")
            outF.write("To fill soil profile (mm): " + str(fill_prof)+ "\n")
    else:
        outF.write("The field does not need to be irrigated in next 7 days."+ "\n")

    outF.close()
    
