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
# In order to personnalize maps, user has to choose the variables that follow
###################
# Meteorological variables choices

# User can use Temperature or Precipitation variable (limited to the files provided on original project)

while True :
    variable_input = input(">>> Choose a variable : TMIN (Daily Temperature Min) ; TMAX (Daily Temperature Max) or P (Daily Precipitation Cumulation)  = ")
    if variable_input == 'TMAX' :

        variable_name = 'tasmaxAdjust'# name of the variable in NetCDF files
        unit = '°C'
        color_continuous_scale = ['#A6A6A6','#4C7F13', '#002b14']
        break

    if variable_input == 'P' :
        variable_name = "prAdjust" # name of the variable in NetCDF files 
        unit = 'mm/day'
        color_continuous_scale = ['#A6A6A6','#06527C', '#032B41']
        break

    if variable_input == 'TMIN' :
        variable_name = 'tasminAdjust' # name of the variable ine NetCDF files
        unit = '°C'
        color_continuous_scale = ['#A6A6A6','#06527C', '#032B41']
        break

    else :
        print("Error: Please choose TMIN, TMAX or P.")

# User can choose the threshold which will be studied	
threshold = int(input(">>> Choose the threshold of the studied variable; (recommended : 30 (Temperature Max) ; 0 (Temperature Min) or 50 (Precipitation)) = "))

# User can personnalized the maximum scale of the map (in order to have a )
# If user says no, the maximum will be automatically provided considering the data computed
while True :
    yn_max_scale = input(" >>> Do you wish to choose the maximum scale ? (Y/N) = ")

    if yn_max_scale == 'Y' :
        max_scale = int(input(" >>> Choose the maximum scale = "))
        break

    if yn_max_scale == 'N' :
        print(" Your choice has been saved.")
        break

    else :
        print("Error: Please answer Y or N to the previous question.")


###################
# Text choice
text_description = ""

###################
# Temporal variables choices : setting period, legend title and folders where the data is

while True : 

    start_year = input(">>> Write the start year (YYYY) (between 2006 and 2019 or 2036 and 2059) = ")
    start_date = start_year +"0101"

    if int(start_year) <= 2019 and int(start_year) >= 2006:

        while True :

            end_year = input(f">>> Write the end year (YYYY) (between {int(start_year) + 1} and 2020) = ")
            end_date = end_year +"0101"     

            if int(end_year) <= 2020 and int(end_year) >= int(start_year):

                if variable_input != 'TMIN':
                    legend = f'Days with - {round(threshold)}{unit} (between {start_year} and {end_year})'

                if variable_input == 'TMAX' or 'P':
                    legend = f'Days with + {round(threshold)}{unit} (between {start_year} and {end_year})'

                period = 'histo'
                filename = f'./data/{variable_name}/{period}_projections/*.nc'
                # Located files where we will get the data

                break 

            else :
                print(f"Please enter a date between {start_year} and 2020.")

        break

    if int(start_year) <= 2059 and int(start_year) >= 2036   :

        while True :

            end_year = input(f">>> Write the end year (YYYY) (between {int(start_year) + 1} and 2060) = ")
            end_date = end_year +"0101" 

            if int(end_year) <= 2060 and int(end_year) >= int(start_year): 
                period = input('>>> Choose the scenario name (RCP45; RCP60; RCP85) = ')

                if variable_input != 'TMIN':
                    legend = f'Days with - {round(threshold)}{unit} (between {start_year} and {end_year}) ({period})'

                if variable_input == 'TMAX' or 'P':
                    legend = f'Days with + {round(threshold)}{unit} (between {start_year} and {end_year}) ({period})'

                                
                filename = f'./data/{variable_name}/{period}_projections/*.nc'
                # Located files where we will get the data

                break

            else:
                print(f"Please enter a date between {start_year} and 2060.")

        break

    else :
        print("Please enter a date between 2006 and 2019 or between 2036 and 2059.")



# Computing number of years, will be necessary to compute year average
years_number = int(f'{end_date[:4]}') - int(f'{start_date[:4]}')

print(f"Your map will be displayed on {years_number} year(s).")

##################
# Asking user if he wants to have location markers
while True :
    location_marker = input(">>> Would you like to display location markers on your map ? (Y/N) = ")

    if location_marker == 'N' : # user doesn't want any location marker

        list_of_latitudes = []
        list_of_longitudes = []
        color_list = []
        text_marker = []
        marker_size  = []

        print("Your choice has been saved.")
        
        break

    if location_marker == "Y" : # user wants to display locations markers
        locations_csv = pd.read_csv('locations.csv', sep = ';')

        list_of_latitudes = locations_csv['list_of_latitudes'].to_list()
        list_of_longitudes = locations_csv['list_of_longitudes'].to_list()
        color_list = locations_csv['color_list'].to_list()
        text_marker = locations_csv['text_marker'].to_list()
        marker_size = locations_csv['marker_size'].to_list()
        
        break

    else : 
        print("Error: Please answer Y or N at the previous question.")
        
        
##################
# Final user choice of custom map 

user_choice = choropleth_function(

    variable_input, variable_name, unit, threshold,
    start_date, end_date, years_number,
    text_description, period, legend, filename,
    location_marker, text_marker, list_of_latitudes, list_of_longitudes, color_list, marker_size,
    color_continuous_scale

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

ds = user_choice.open_files()

df = user_choice.files_location_points(ds)

initial_european_data = user_choice.european_area(df)

######################################################
# Chosen variable computation on temporal range

if variable_input == "TMAX" :
    final_european_data = user_choice.temperature_max_computation(ds, initial_european_data)

if variable_input == "P":
    final_european_data =  user_choice.precipitation_computation(ds, initial_european_data)

if variable_input == "TMIN" :
    final_european_data = user_choice.temperature_min_computation(ds, initial_european_data)

######################################################
# Chosen variable computation on geographical range

data = user_choice.data_with_index(final_european_data, geo_data_used_without_index)

data_without_index = user_choice.data_without_index(data)

maxi = user_choice.data_max(data)

######################################################
# Choropleth map with markers

if location_marker == 'Y':
    if yn_max_scale == 'Y' : 
        output_with_markers = user_choice.choropleth_map_with_markers(data, geo_data_used, max_scale)
    if yn_max_scale == 'N':
        output_with_markers = user_choice.choropleth_map_with_markers(data, geo_data_used, maxi)

# Choropleth map without markers

if location_marker == 'N':
    if yn_max_scale == 'Y' : 
        output_with_markers = user_choice.choropleth_map_without_marker(data, geo_data_used, max_scale)

    if yn_max_scale == 'N' :
        output_without_marker = user_choice.choropleth_map_without_marker(data, geo_data_used, maxi)

######################################################

print('*** Process successfully achieved. Check folders to see output. ***')