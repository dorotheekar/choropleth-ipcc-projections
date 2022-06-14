import pandas as pd
import xarray as xr
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from shapely.geometry import Point
from geopandas import GeoDataFrame
from shapely.ops import nearest_points
from shapely.geometry import MultiPoint


from main import choropleth_function

############################################################
# VARIABLES INITIALIZATION

############################
# BEGINNING OF USER CHOICES
# > In order to personnalize maps, user is allowed to choose the variables that follow
###################
# Meteorological variables choices

# User can use Temperature or Precipitation variable (limited to the files provided on original project)

while True :
    variable_input = input(">>> Choose a variable : T (Daily Temperature Max) or P (Daily Precipitation Cumulation) = ")
    if variable_input == 'T' :

        variable_name = 'tasmaxAdjust'# name of the variable in NetCDF files
        unit = '°C'
        break

    if variable_input == 'P' :
        variable_name = "prAdjust" # name of the variable in NetCDF files 
        unit = 'mm/day'
        break

    else :
        print("Error: Please answer T or P to the previous question.")

# User can choose the threshold which will be studied	
threshold = int(input(">>> Choose the studied variable threshold. (recommended : 30 (Temperature) or 50 (Precipitation)) = "))

###################
# Text choice
text_description = ""

###################
# Type of projection choice
RCP = input('>>> Choose the scenario name (historical; RCP45; RCP60; RCP85) = ')

###################
# Temporal variables choices : setting period, legend title and folders where the data is
start_date = input(">>> Write the start year (YYYY) (between 2010 and 2019 or 2045 and 2055) = ")+"0101"

if int(f'{start_date[:4]}') < 2022:
    end_date = input(f">>> Write the end year (YYYY) (between {int(start_date[:4]) + 1} and 2019) = ") +"0101"    
    period = 'histo'
    legend = f'Days with + {round(threshold)}{unit} (between {start_date[:4]} and {end_date[:4]})'
    filename = f'./data/{variable_name}/{period}_projections/*.nc'
    # Located files where we will get the data

else :
    end_date = input(f">>> Write the end year (YYYY) (between {int(start_date[:4]) + 1} and 2055) = ") +"0101"
    period = RCP
    legend = f'Days with + {round(threshold)}{unit} (between {start_date[:4]} and {end_date[:4]}) ({period})'
    filename = f'./data/{variable_name}/{period}_projections/*.nc'
    # Located files where we will get the data

years_number = int(f'{end_date[:4]}') - int(f'{start_date[:4]}')

print(f"Your map will be displayed on {years_number} year(s).")

##################
# Custom location points

# Initialisation of those variables. Those won't be needed if the user decides to have no marker on the map
list_of_latitudes = []
list_of_longitudes = []
color_list =[]
text_marker =[]
marker_size = []
custom=[]
#

# Asking user if he wants to have location markers
while True :
    location_marker = input(">>> Would you like to display location markers on your map ? (Y/N) = ")

    if location_marker == 'N' : # user doesn't want any location marker
        print("Your choice has been successfully saved.")
        
        break

    if location_marker == "Y" : # user wants to display locations markers
        custom = input(">>> Would you like to custom your location markers ? (Y/N) = ")
        
        if custom == "Y" : # user want to custom location markers

            n = int(input(">>> How many points do you want to display ? "))

            for i in range(0, n):
                city = input('>> Enter location name = ') # give the city name on the marker
                text_marker.append(city)

                lat = float(input('>> Enter the corresponding latitude = ')) 
                list_of_latitudes.append(lat)

                lon = float(input('>> Enter the corresponding longitude = '))
                list_of_longitudes.append(lon)

                color_pt = input('>> Enter the corresponding color (red or yellow) = ' ) # any other color could be chosen
                color_list.append(color_pt)


            marker_size = int(input('>> Specify the marker size (recommended : 12) = '))
            print("Your choice has been successfully saved.")
            break

        if custom  == "N" :
            print('>> Markers will be: Rouen, Lyon, Paris, Porto, Milan.')

            list_of_latitudes = [48.879349, 45.441975, 48.772090, 41.264996, 45.457721 ]
            list_of_longitudes = [2.196998,  6.382717, 2.549041, -8.595143, 9.602173]
            color_list = ['red', 'red', 'yellow', 'yellow', 'yellow']
            marker_size = 12
            text_marker = ['Rouen', 'Lyon', 'Paris', 'Porto', 'Milan']

            
            break

        else :
            print("Error: Please answer Y or N at the previous question.")
            
    else : 
        print("Error: Please answer Y or N at the previous question.")
        
##################
# Final user choice of custom map 


user_choice = choropleth_function(

    variable_input, variable_name, unit, threshold,
    start_date, end_date, years_number,
    text_description, RCP, period, legend, filename,
    text_marker, location_marker, custom, list_of_latitudes, list_of_longitudes, color_list, marker_size

    )

##################
# Choice of european map division

geo_data_used, geo_data_used_without_index = user_choice.map_division()

# END OF USER CHOICES
######################################################
# START OF MODULE PROCESS 
#
print('*** All choices have been saved. Beginning of the process ... ***')

##################
# File opening and data extraction
# Please refer to main.py for a better understand of functions

ds = user_choice.open_file()

df = user_choice.files_location_points(ds)

initial_european_data = user_choice.european_area(df)

######################################################
# Chosen variable computation on temporal range

if variable_input == "T" :
    final_european_data = user_choice.temperature_computation(ds, initial_european_data)

if variable_input == "P":
    final_european_data =  user_choice.precipitation_computation(ds, initial_european_data)

######################################################
# Chosen variable computation on geographical range

data = user_choice.data_with_index(final_european_data, geo_data_used_without_index)

data_without_index = user_choice.data_without_index(data)

maxi = user_choice.data_max(final_european_data)

######################################################
# Choropleth map with markers

if location_marker == 'Y':
    output_with_markers = user_choice.choropleth_map_with_markers(data, geo_data_used, maxi)

# Choropleth map without markers

if location_marker == 'N':
    output_without_marker = user_choice.choropleth_map_without_marker(data, geo_data_used, maxi)

######################################################

print('*** Process successfully achieved. Check folders to see output. ***')