# Chloropeth map of IPCC projection precipitation and temperature scenarios managing NetCDF files

## Introduction

The provided maps are based on Eurocordex NetCDF files on adjusted IPCC models (https://www.euro-cordex.net/060378/index.php.en) and display 
the number of days the meteorological variable is above the threshold (example : Maximum daily max temperature > 30°c). 
Variable, threshold and time intervall are to be chosen by user. Some custom localization markers can be added.

## Table of contents

* [Technology] (#technology)
* [Setup] (#setup)
* [Folder structure] (#folder-structure)
* [Files description] (#files-description)

## Technology 

Project created with :
Python 3.9.13

## Setup

Please note that geopandas module sometimes can't be just installed with pip install geopandas. This requires to download wheel dependecies such as : 
Fiona, DAL, pyproj, rtree, and shapely (provided here : https://www.lfd.uci.edu/~gohlke/pythonlibs/). It should match your architecture and python version. 
When each wheel is downloaded, please open a command prompt and change directories to the folder where they are located. 
Run for each one of them ```pip install wheel_filename.whl```.
		
When this process is complete, you can properly ```pip install -r requirements.txt``` in order to install geopandas and all other necessary modules.

## Folder structure
```
├── README.txt          
├── data
│   ├── prAdjust 
│   │  │
│   │  ├── histo_projections : *.nc
│   │  │
│   │  └── RCP85_projections : *.nc
│   │
│   │
│   └── tasmaxAdjust
│      │
│      ├── histo_projections : *.nc
│      │
│      └── RCP85_projections : *.nc
│
├── input.py              
├── main.py             
├── requirements.txt                          
├── nutsrg_1.json         
├── nutsrg_2.json            
└── europe.geojson   
```
## Files description

* Data : Note that anyone could had  other files with other temporal range or other variables respecting
	   folder structure below.

	- ```prAdjust``` : daily precipitation adjusted model 

				```data/histo-projections/*.nc``` : .nc files on temporal range 2006 to 2020
				```data/RCP85-projections/*.nc``` : .nc files on temporal range 2036 to 2060

	- ```tasmaxAdjust``` : daily maximum temperature adjusted model

				```data/histo-projections/*.nc``` : .nc files on temporal range 2006 to 2020
				```data/RCP85-projections/*.nc``` : .nc files on temporal range 2036 to 2060

	- ```tasminAdjust``` : daily minimum temperature adjusted model

				```data/histo-projections/*.nc``` : .nc files on temporal range 2006 to 2020 
				```data/RCP85-projections/*.nc``` : .nc files on temporal range 2036 to 2060
* Input : 

	- ```input.py``` : list of variables chosen by user
			= variable_input : Variable name studied (NetCDF files here provide only precipitation cumulation per day, temperature maximum per day, temperature minimum per day).
			= threshold : Threshold studied considering the variable chosen.
			= start_date : Start date of the period studied.
			= end_date : End date of the period studied.
			= RCP : Name of the scenario projection. It is useful to get to the corresponding folder and will appear on the map. (The original project provides only RCP85 projection)

			= location_marker : Asking the user if he wants to display a map with marker or not.
			= custom : Asking the user if he wants to display a map with custom markers.
			= text_marker : User needs to choose marker names.
			= list_of_latitudes : User needs to enter the each latitude for markers.
			= list_of_longitudes : User needs to enter the each longitude for markers.
			= color_list : User needs to enter the each color for markers.
			= marker_size : User needs to choose one marker size.

* Module :

	- ```main.py``` : contains all custom modules to provide choropleth map.

* Output : choropleth maps in html depending on variables chosen by user.

	- ```{variable_name}_{period}_{threshold}_without_marker.html``` : choropleth map specified without any marker
	- ```{variable_name}_{period}_{threshold}_with_marker.html``` : choropleth map specified with markers

* Requirements : 

	-  ```requirements.txt``` : 	
```
		= pandas
		= xarray
		= numpy
		= geopandas
		= plotly
		= shapely
		= netCDF
		= dask
```
* Geographical data : files used to parse data according to geographical division chosen by the user

	- ```nutsrg1.json``` : a .json file providing a regions enlarged division of Europe
	- ```nutsrg2.json``` : a .json file providing a regions division of Europe
	- ```europe.geojson``` : a .geojson file providing a countries division of Europe

         
