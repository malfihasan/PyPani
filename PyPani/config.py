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

class UAF_config(object):
    def __init__(self, day, month, year, pjday, pyr, txt_file=False):
        self.month = month # Month value for current date
        self.day = day # Day value for current date 
        self.year = year # Year value for current date
        self.planting_jday = pjday # Planting Julian day 
        self.planting_year = pyr # Planting Year 

        if not txt_file :  
            self.id_txt = "Station_01: Crop Field 01" # User defined process/field name 
            self.lat = 23.7951 # Lattitude [ default latitude for Barishal, Bangladesh ]
            self.elev = 5.     # Elevation [ default elevation for Barishal, Bangladesh ]
            self.obs_weather_file = "tests/required/Observed_weather_station_02.csv" # Observed weather file
            self.pred_weather_file = "tests/required/Forcast_n_obs_weather_station_01.csv" # Predicted/Forecasted weather file
            self.pet_cal_method = "PTM" # PET calculation method. There are different requirement for each methods
                                        # Three options available so far:  
                                        ##  Type 1 : Penman-Monteith Method ( PMM )
                                        ##  Type 2 : Preistly-Taylor Method  ( PTM )
                                        ##  Type 3 : Blainy-Criddle Method ( BCM )
            self.crop = "wheat" # Crop type 

            self.ksp_file = "tests/required/ksp.csv" # KSP coefficient/ Ground cover file 
            self.rainfall_file = "tests/required/rainfall.csv" # Rainfall file
            self.irrg_file = "tests/required/irrg.csv" # Irrigation file
            self.sm_file = "tests/required/sm.csv" # Soil moisture file
            self.max_irrg = 100.0 # Maximum allowable irrigation [ values are in mm ] 
            self.soil_type = "silt" # Soil type
            self.planting_sm = 40 # Soil moisture at planting [ values are in percentage ]
            self.water_table = 2.0 # Water table NA or any depth at (m)[ values are in mm ]
            self.outfile = "tests/output.csv" # Outputfile required? 
            self.recom = "tests/recommend.txt" # Name of recommendation file 
        else:
            pass # For now !!!!! 
                 # TO DO : read a txt_file and populate same data as above. 

# A class for KSP curve 
class crop_growth(object):
    def __init__(self, crop_name):
        self.crop_name = crop_name
        if crop_name == "maize":
            self.val_ksp = [0, 0,   10,  28,  74,  85,   85,   67,    0 ]
            self.GDD_ksp = [0, 88, 300, 500, 800, 950, 1122, 1400, 2000 ]
            self.base = 10
        elif crop_name == "wheat":
            self.val_ksp = [0, 0,    4,  12,  72,   80,   75,   46,    0 ]
            self.GDD_ksp = [0, 97, 300, 450, 850, 1000, 1464, 1750, 2200 ]            
            self.base = 0
            
    def find_stage(self, sGDD):
      
        if (self.crop_name == "maize"):
            if sGDD <= 88 :
                phase = 0
            elif (sGDD > 88) and (sGDD <= 1122):
                phase = 1
            elif (sGDD > 1122) and (sGDD <= 2000):
                phase = 2 
            elif (sGDD > 2000) :
                phase = 3
        elif (self.crop_name == "wheat"):
            if sGDD <= 97 :
                phase = 0
            elif (sGDD > 97) and (sGDD <= 1464):
                phase = 1
            elif (sGDD > 1464) and (sGDD <= 2200):
                phase = 2 
            elif (sGDD > 2200) :
                phase = 3
                
        return phase
    
    def print_growth(self, txt):
        #print(self.crop_name)
        if (self.crop_name == "maize"):
            return( txt + " " + self.crop_name )
        elif (self.crop_name == "wheat"):
            return( txt + " + O_O + " + self.crop_name )



# A class for Soil
class soil_profile(object):
    def __init__(self, soil_name):
        self.soil_name = soil_name
        '''
        surf_depth --> silt, mm (2.02 in)
        deep_depth --> deep profile, mm (3 ft - SURFDEPTH)
        paw --> silt, mm water/mm soil
        max_deep (SW) --> silt, mm (5.95 in)
        u --> silt, mm (0.35 in)
        alpha --> silt, mm/SQRT(day)
        '''
        if soil_name == "clay":
            self.surf_depth = 42.9
            self.deep_depth = 871.5
            self.paw = 0.14
            self.max_deep = 121.9
            self.u = 6.0
            self.alpha = 3.50
            self.zmax = 2.0 
        elif soil_name == "clay_loam":
            self.surf_depth = 59.9
            self.deep_depth = 854.5
            self.paw = 0.2
            self.max_deep = 170.9
            self.u = 12.0
            self.alpha = 5.08
            self.zmax = 6.48
        elif soil_name == "sandy_clay_loam":
            self.surf_depth = 51.3
            self.deep_depth = 863.1
            self.paw = 0.175
            self.max_deep = 151.1
            self.u = 9.0
            self.alpha = 4.04
            self.zmax = 6.93
        elif soil_name == "sandy_loam":
            self.surf_depth = 50.8
            self.deep_depth = 853.6
            self.paw = 0.15
            self.max_deep = 129.5
            self.u = 7.5
            self.alpha = 3.79
            self.zmax = 6.17
        elif soil_name == "loam_sand":
            self.surf_depth = 65.0
            self.deep_depth = 849.4
            self.paw = 0.1
            self.max_deep = 84.8
            self.u = 6.5
            self.alpha = 3.52
            self.zmax = 5.33
        elif soil_name == "sand":
            self.surf_depth = 80.0
            self.deep_depth = 834.4
            self.paw = 0.075
            self.max_deep = 62.5
            self.u = 6.0
            self.alpha = 3.34
            self.zmax = 4.19
        elif soil_name == "silty_clay_loam":
            self.surf_depth = 59.9
            self.deep_depth = 854.5
            self.paw = 0.2
            self.max_deep = 170.9
            self.u = 12.0
            self.alpha = 5.08
            self.zmax = 6.48
        elif soil_name == "silty_loam":
            self.surf_depth = 51.3
            self.deep_depth = 863.1
            self.paw = 0.175
            self.max_deep = 151.1
            self.u = 9.0
            self.alpha = 4.04
            self.zmax = 6.93
        elif soil_name == "silt":
            self.surf_depth = 51.3
            self.deep_depth = 863.1
            self.paw = 0.175
            self.max_deep = 151.1
            self.u = 9.0
            self.alpha = 4.04
            self.zmax = 6.93      
