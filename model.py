'''
__name__: PANI-py
__developer__ : M. Alfi Hasan
__developer_contact__: mdalfihasan19@gmail.com <malfihasan.com>
__python_version__: 3.5
__partner__: CIMMYT Bangladesh
__update_date__: 30 July, 2020
__version__: 1.01
'''

### Please Adjust default config for your need.

import os
import argparse
import PyPani as PP

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("target_date", type=str, help="Provide target date as MM/DD/YYYY format"  )
    parser.add_argument("pl_date", type=str, help="Provide planting date as JulianDay/YYYY format" )


    args = parser.parse_args()
    monthX, dayX, yearX = list((args.target_date).split("/"))
    pl_Jday, pl_year = list((args.pl_date).split("/"))
    

    PP.recommendation_engine( int(dayX), int(monthX), int(yearX), int(pl_Jday), int(pl_year))


