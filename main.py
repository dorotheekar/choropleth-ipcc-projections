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

######################################################################
class choropleth_function:
# Choropleth class function

    ######################################################################
    def __init__(self,
    variable_input, variable_name, unit, threshold, # meteorological variables
    start_date, end_date, years_number, # temporal variables
    text_description, period, legend, filename, # description variables
    text_marker, location_marker, list_of_latitudes, list_of_longitudes, color_list, marker_size,# marker variables
    color_continuous_scale) : 

    # Variables will be chosen by the user in the input file

        self.variable_input = variable_input
        self.variable_name = variable_name
        self.unit = unit
        self.threshold = threshold
        self.start_date = start_date
        self.end_date = end_date
        self.years_number = years_number
        self.period = period
        self.legend = legend
        self.filename = filename
        self.location_marker = location_marker
        self.list_of_latitudes = list_of_latitudes
        self.list_of_longitudes = list_of_longitudes
        self.color_list = color_list
        self.text_description = text_description
        self.text_marker = text_marker
        self.marker_size = marker_size
        self.color_continuous_scale = color_continuous_scale

    ######################################################################        
    def map_division(self):
    # Chosing .json file where the data will be displayed (here we only have european ones for personal purposes)

        while True:
            geo_data = input(">>> Choose a european map divison: C (Countries) / R (Regions) / ER (Enlarged Regions) = ")
            # User is choosing between 3 given choice of map division

            if geo_data == 'C': 
                # European Countries division

                geo_data_used = gpd.read_file('europe.geojson')
                geo_data_used = geo_data_used.set_index(['UN']).sort_values(by = ['UN'])
                geo_data_used_without_index = geo_data_used.reset_index()

                print("Your choice has been successfully saved.")
                return geo_data_used, geo_data_used_without_index

            if geo_data == 'R':
                # European Regions division

                geo_data_used = gpd.read_file('nutsrg_2.json')
                geo_data_used = geo_data_used.sort_values(by = ['id']).set_index(['id'])
                geo_data_used_without_index = geo_data_used.reset_index()

                print("Your choice has been successfully saved.")
                return geo_data_used, geo_data_used_without_index 

            if geo_data == 'ER':
                # Enlarged European Regions division

                geo_data_used = gpd.read_file('nutsrg_1.json')
                geo_data_used = geo_data_used.sort_values(by = ['id']).set_index(['id'])
                geo_data_used_without_index  = geo_data_used.reset_index()

                print("Your choice has been successfully saved.")
                return geo_data_used, geo_data_used_without_index

            else :
                print('Error: Please answer C or R or ER to the previous question.')

    ######################################################################
    def open_file(self):
    # NetCDF Files opening sliced by start date, end date, european latitude and longitude

        print("> Files opening in progress...")

        ds = xr.open_mfdataset(self.filename, autoclose=True)
        ds = ds.sel(time = slice(self.start_date, self.end_date), rlat=slice(-15, 20), rlon=slice(-20,15))
        ds = ds.load() # Loading sliced files in RAM 

        print("> Files successfully opened.")

        return ds

    ######################################################################
    def files_location_points(self, ds):
    # Extraction of longitude and latitude of netCDF files

        print('> Files location points extraction in progress...')

        df= pd.DataFrame()

        lon = ds.lon.values
        lat = ds.lat.values

        rlat_list, rlon_list, lat_list, lon_list =[], [], [], []

        for x, y in [(x,y) for x in ds.rlat.values for y in ds.rlon.values]:
            # Loop will extract longitude and latitude values given in NetCDF files
            # Be aware that not all NetCDF files contain rlon and rlat

            rlat_list.append(x)
            rlon_list.append(y)

            local_ds=ds.sel(rlat=x,rlon=y)
            lat_list.append(local_ds.lat.values)
            lon_list.append(local_ds.lon.values)

        df = pd.DataFrame(
        # Dataframe will contain all values of lat, lon, rlat and rlon given in sliced NetCDF

           {
              "lat": lat_list,
              "lon": lon_list,
              "rlat": rlat_list,
               "rlon" : rlon_list
           })

        print("> Location points successfully extracted from files.")

        return df

    ######################################################################
    def european_area(self, df):
    # Extraction of file points on european area (!!!Missing Russia and Iceland!!!)

        print('> European location points extraction in progress...')

        geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
        df_tmp = df.drop(['rlon', 'rlat', 'lon', 'lat'], axis = 1)
        gdf = GeoDataFrame(df, crs = "EPSG:4326", geometry = geometry)
        # Create a geodataframe with all given latitudes and longitudes in df 

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))    
        bords_europe = world[world.continent=="Europe"]
        bords_europe = bords_europe[(bords_europe.name!="Russia") & (bords_europe.name!= "Iceland")].drop(['pop_est', 'continent','name','iso_a3','gdp_md_est'], axis = 1)
        # Save all POINTS in Europe area

        initial_european_data = gpd.sjoin(gdf, bords_europe, op = "within")
        initial_european_data = initial_european_data.drop(['index_right'], axis = 1)
        # Merge the two previous geodataframe to keep only the european POINTS for which we have data

        print("> European location points successfully extracted.")

        return initial_european_data

    ######################################################################
    def temperature_max_computation(self, ds, initial_european_data):
    # Number of days with temperature above the threshold computation on temporal range (by POINTS)

        print("> Temperature days computation on geographical range in progress...") 

        SummList = []
        for i in range(len(initial_european_data)):
            # Loop will search for every POINT (rlat, rlon) the corresponding data

            vals = ds.sel(rlat = initial_european_data['rlat'].iloc[i], rlon = initial_european_data['rlon'].iloc[i])[self.variable_name].values
            su = [1 if v - 273.15 >= self.threshold else 0 for v in vals] 
            # We aim at counting the days that respect the threshold given by the user
            # As we will give the temperature in celsius degree we convert 0 °C + 273.15 = 273.15 K

            SummList.append(sum(su) / self.years_number)
            # This is the average days by year the respect the threshold given

        initial_european_data[self.legend] = SummList
        # Saving the list of data in final dataframe

        print("> Temperature days successfully computed on geographical range.") 

        return initial_european_data

    ######################################################################
    def temperature_min_computation(self, ds, initial_european_data):
    # Number of days with temperature above the threshold computation on temporal range (by POINTS)

        print("> Temperature days computation on geographical range in progress...") 

        MinList = []
        for i in range(len(initial_european_data)):
            # Loop will search for every POINT (rlat, rlon) the corresponding data

            vals = ds.sel(rlat = initial_european_data['rlat'].iloc[i], rlon = initial_european_data['rlon'].iloc[i])[self.variable_name].values
            su = [1 if v - 273.15 <= self.threshold else 0 for v in vals] 
            # We aim at counting the days that respect the threshold given by the user
            # As we will give the temperature in celsius degree we convert 0 °C + 273.15 = 273.15 K

            MinList.append(sum(su) / self.years_number)
            # This is the average days by year the respect the threshold given

        initial_european_data[self.legend] = MinList
        # Saving the list of data in final dataframe

        print("> Temperature days successfully computed on geographical range.") 

        return initial_european_data

    ######################################################################
    def precipitation_computation(self,  ds, initial_european_data):
    # Number of days with precipitation above the threshold computation on temporal range (by POINTS)

        print("> Precipitation days computation on geographical range in progress...") 

        PrecipList = []
        for i in range(len(initial_european_data)):
        # Loop will search for every POINT (rlat, rlon) the corresponding data

            vals = ds.sel(rlat = initial_european_data['rlat'].iloc[i], rlon = initial_european_data['rlon'].iloc[i])[self.variable_name].values
            su = [1 if v * 86400 >= self.threshold else 0 for v in vals] 
            # We aim at counting the days that respect the threshold given by the user
            # As we will give the temperature in celsius degree we convert 0 °C + 273.15 = 273.15 K

            PrecipList.append(sum(su) / self.years_number)
            # This is the average days by year the respect the threshold given

        initial_european_data[self.legend] = PrecipList
        # Saving the list of data in final dataframe

        print("> Precipitation days successfully computed on geographical range.") 

        return initial_european_data


    ######################################################################
    def data_with_index(self, final_european_data, geo_data_used_without_index):
    # Maximum of days in POLYGON

        print('> Region data computation in progress...') 

        datum = []
        # Initialized list

        for ligne in range(len(geo_data_used_without_index)):
        # Loop will provide the maximum data by each geographical division

            pip_data = final_european_data.loc[final_european_data.within(geo_data_used_without_index.loc[ligne, 'geometry'])]
            # Verify if POINT is contained in POLYGONS of the geodataframe that the user chose

            datum.append(pip_data[self.legend].mean()) 
            # Keep the mean of the POLYGON

        data = pd.DataFrame(datum)
        data['id'] = geo_data_used_without_index['id']
        data['geometry'] = geo_data_used_without_index['geometry']
        data[self.legend] = data[0]
        data['na'] = geo_data_used_without_index['na']

        data = data.sort_values(by =['id']).set_index(['id'])

        print('> Region data successfully computed.') 

        return data

    ######################################################################
    def data_without_index(self, data):
    # Save dataframe without index (will be used choropleth function)

        data_without_index = data.reset_index()
        return data_without_index

    ######################################################################
    def data_max(self, data):
    # Save data maximum (in order to custom it on choropleth map)

        return data [self.legend].max()

    ######################################################################
    def choropleth_map_without_marker(self, data, geo_data_used, maxi):
    # Write an html file for choropleth map (without marker)  

        print('> Map in creation...')

        fig_without_marker = go.Figure(px.choropleth_mapbox(data_frame = data, # data by the region of geodataframe chosen
            locations = data.index,
            geojson = geo_data_used,# geodataframe chose
            color = self.legend, # custom legend
            hover_name = 'na',
            title = self.legend, # custom legend 
            mapbox_style ='carto-positron',
            center = {'lat':47, 'lon':6},
            zoom = 3.2,
            opacity = 1,
            color_continuous_scale = self.color_continuous_scale,
            range_color = [0, maxi]
            ))

        fig_without_marker.update_geos(fitbounds = "locations")
        fig_without_marker.update_layout(title_text = self.legend, title_x = 0.5)
        fig_without_marker.write_html(f"{self.variable_name}_{self.period}_{self.threshold}_without_marker.html")
        # The ouput will be given a specific name corresponding to the variable choices

        print('> Map created.')

    ######################################################################   
    def choropleth_map_with_markers(self, data, geo_data_used, maxi):
    # Write an html file for choropleth map (with markers)

        print('> Map in creation...')

        fig_with_markers= go.Figure(

            px.choropleth_mapbox(
                data_frame = data, # data by the region of geodataframe chosen
                locations = data.index,
                geojson = geo_data_used, #geodataframe chosen
                color = self.legend, # custom legend 
                hover_name = 'na',
                title = self.legend, # custom legend
                mapbox_style = 'carto-positron',
                center = {'lat':47, 'lon':6},
                zoom = 3.2,
                opacity = 1,
                color_continuous_scale = self.color_continuous_scale,
                range_color = [0, maxi]

            )
        )

        fig_with_markers.update_geos(fitbounds = "locations")
        fig_with_markers.update_layout(title_text = self.legend, title_x = 0.5)

        fig_with_markers.add_scattermapbox(

            lat = self.list_of_latitudes,
            lon = self.list_of_longitudes,
            mode = 'markers+text',
            text = self.text_marker,
            below ='',
            marker_size = self.marker_size,
            marker_color = self.color_list
         )

        fig_with_markers.write_html(f"{self.variable_name}_{self.period}_{self.threshold}_with_markers.html")
        # The ouput will be given a specific name corresponding to the variable choices

        print('> Map created.')