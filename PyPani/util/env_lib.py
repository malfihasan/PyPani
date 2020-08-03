'''
__name__: PANI-py
__file_description__: This is the ground cover, rainfall, irrigation and soil moiesture module for PANI-py.  
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

# A function for GDD 
def GDD_calculation(doy_pred, tmp_avg_pred, crop_base_in, crop_i_in):
    ksp_int = []
    ksp = []
    accGDD = 0
    sumGDD = []
    phase_i =[]
    n = 0 
    result_dict = dict()
    for i in range(0, len(doy_pred)):
        gdd = tmp_avg_pred[i] - crop_base_in
        if gdd < 0 : gdd = 0 
        accGDD = accGDD + gdd
        sumGDD.append(accGDD)
        
        phase_i.append( crop_i_in.find_stage(sumGDD[i]) )

        highest_GDDksp = crop_i_in.GDD_ksp[8]
        
        if sumGDD[i] > highest_GDDksp : 
            ksp_int.append(crop_i_in.val_ksp[8])
            ksp.append(ksp_int[n])
            n+=1
        else:
            for m in range(0,8):
                #print(m)
                if (sumGDD[i] >= crop_i_in.GDD_ksp[m]) and (sumGDD[i] <= crop_i_in.GDD_ksp[(m+1)]) :
                    tmp_cal = crop_i_in.val_ksp[m] + ( crop_i_in.val_ksp[m+1] - \
                                        crop_i_in.val_ksp[m]*( (sumGDD[i] - crop_i_in.GDD_ksp[m])/(crop_i_in.GDD_ksp[m+1] - crop_i_in.GDD_ksp[m])  ) )
                
                    ksp_int.append( tmp_cal  )
                    ksp.append(ksp_int[n])
                    n+=1
                    break

    result_dict['KSP_INT'] = ksp_int
    result_dict['KSP'] = ksp
    result_dict['ACC_GDD'] = accGDD
    result_dict['SUM_GDD'] = sumGDD
    result_dict['PHASE_I'] = phase_i

    return result_dict


# replacing given GC values 
# finding the values from the file
def update_observed_GC( ksp_file, doy_pred, ksp ):
    
    result_dict = dict()

    df_gc = pd.read_csv( ksp_file  )

    if len(df_gc['jday']) > 0 : 
        jday_tmp = list(df_gc['jday'])
        sel_ind = []
        for j in jday_tmp: 
            i_n = [ i for i in range(len(doy_pred)) if doy_pred[i]==j  ]
            sel_ind.append(i_n[0])
    else:
        print("The KSP file is empty!!!")

    ksp_new = ksp.copy()
    if (len(sel_ind) > 0 ): 
        for jn, k in enumerate(sel_ind):
            ksp_new[k] = list(df_gc['gc_value'])[jn]
    else:
        print("No Match for current GC and weather data!!")

    # removing more than 100 ground cover from the values
    ksp_new = [ 100.0 if i > 100.0 else i for i in ksp_new ]

    result_dict['KSP_NEW'] = ksp_new

    return result_dict


def update_observed_rainfall( rainfall_file, doy, sel_yr ):

    result_dict = dict()

    rain_mm = [None]*len(doy)

    df_rain = pd.read_csv( rainfall_file )

    # merging the rainfall data with current doy 
    for i, doy_l in enumerate(doy):
        df_tmp = df_rain[(df_rain['jday']==doy_l) & (df_rain['year']==sel_yr[i])]
        if (len(df_tmp['jday']) < 1 ):
            print("No precip data found for the date: " + str(doy[i]) + ", " + str(sel_yr[i]) )
        else: 
            rain_mm[i] = list(df_tmp['pcp_value'])[0]
        
    # error check 
    non_rainfall = [ i for i in rain_mm if i is None ]
    if (len(non_rainfall)>0):
        print("The rainfall file has : " + str(len(non_rainfall)) + " missing value.")

    result_dict['RAIN'] = rain_mm

    return result_dict



def update_observed_irrigation( irrg_file, doy, sel_yr ):
    result_dict = dict()

    irrg_mm = [0]*len(doy)
    df_irrg = pd.read_csv( irrg_file)

    # merging the irrigation data with current doy 
    for i, doy_l in enumerate(doy):
        df_tmp = df_irrg[(df_irrg['jday']==doy_l) & (df_irrg['year']==sel_yr[i])]
        if (len(df_tmp['jday']) < 1 ):
            pass
        else: 
            irrg_mm[i] = list(df_tmp['irrg_value'])[0]
            #print(irrg_mm[i])

    result_dict['IRRG'] = irrg_mm

    return result_dict


def update_observed_sm( sm_file):
    result_dict = dict()

    df_sm = pd.read_csv( sm_file )
    if(len(df_sm['sm_value']) < 1):
        print("No manual entry of soil moisture values are not provided.")

    result_dict['SM'] = df_sm

    return result_dict