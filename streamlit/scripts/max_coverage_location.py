import requests
from collections import defaultdict
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='my_app')
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx
import osmnx as ox
import geopandas as gpd
import networkx as nx
from shapely.geometry.polygon import Point, Polygon
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.geometry.multipolygon import MultiPolygon
import folium
import geopandas as gpd
import math
from geopy.distance import distance, great_circle
from haversine import haversine, Unit
import math


class GeocodingError(Exception):
    pass

def main(address,radius_miles,speed):

    if address.strip()=='':
        raise GeocodingError('No address entered, please enter an address')
    
    geolocator = Nominatim(user_agent='my_application')
    location = Nominatim(user_agent='my_app').geocode(address, addressdetails=True)
    if 'city' in location.raw['address']:
        town_city = location.raw['address']['city']
    elif 'town' in location.raw['address']:
        town_city = location.raw['address']['town']
    else:
        town_city = None



    radius_metres = radius_miles*1609

    if location is None:
        raise GeocodingError('Address could not be found, please check the example format {}'.format(address))

    origin = (location.latitude, location.longitude)
    G = ox.graph_from_point(origin, dist=radius_metres, network_type='drive')
    #G = ox.add_edge_speeds(G,speed)
    #G = ox.add_edge_travel_times(G)


    lsoa_data = pd.read_csv('../data/lsoa_global_number_residents_2021.csv')
    lsoa_postcode = pd.read_csv('../data/pcd_lsoa21cd_nov22_en.csv')
    lsoa_pop = pd.read_csv('../data/lsoa_global_number_residents_2021.csv')
    gdf = gpd.read_file('../data/LSOA_Dec_2021_Boundaries_Generalised_Clipped_EW_BGC_2022_5000101660793162025/LSOA_2021_EW_BGC.shp')
    gdf_c= gdf.query("LSOA21NM.str.contains('{}')".format(town_city))
    # set the CRS of the GeoDataFrame to British National Grid (EPSG:27700)
    gdf_c = gdf_c.set_crs(epsg=27700)

    # project the geometry to WGS84 (EPSG:4326)
    gdf_c = gdf_c.to_crs(epsg=4326)


    lsoa_codes = gdf_c['LSOA21CD'].tolist()
    lsoa_data = {lsoa_code: {} for lsoa_code in lsoa_codes}

    for index, row in gdf_c.iterrows():
        lsoa_code = row['LSOA21CD']
        if lsoa_code in lsoa_data:
            lsoa_data[lsoa_code]['Latitude'] = row['geometry'].centroid.y
            lsoa_data[lsoa_code]['Longitude'] = row['geometry'].centroid.x
            node = ox.distance.nearest_nodes(G, row['geometry'].centroid.x, row['geometry'].centroid.y)
            lsoa_data[lsoa_code]['Node'] = node

    lsoa_population = {}
    for lsoa_code in lsoa_data:
        population = lsoa_pop.loc[lsoa_pop['LSOA21CD'] == lsoa_code, 'Population'].iloc[0]
        try:
            latitude = lsoa_data[lsoa_code]['Latitude']
        except KeyError:
            print(f'KeyError: Latitude not found for LSOA code {lsoa_code}')
            latitude = None
        try:
            longitude = lsoa_data[lsoa_code]['Longitude']
        except KeyError:
            print(f'KeyError: Longitude not found for LSOA code {lsoa_code}')
            longitude = None
        lsoa_population[lsoa_code] = {'Population': population, 'Latitude': latitude, 'Longitude': longitude}

    # get LSOAs within search radius
    lsoas_in_radius = []
    for lsoa_code, data in lsoa_data.items():
        distance=haversine(origin, (data['Latitude'], data['Longitude']),unit='km')
        if distance <= radius_metres/1000:
    
            lsoas_in_radius.append(lsoa_code)
          
          
    m = folium.Map(location=origin, zoom_start=12)
    folium.Marker(location=origin, tooltip=address).add_to(m)
    folium.Circle(location=origin, radius=radius_metres, color='red', fill=False, tooltip='Search Radius').add_to(m)

    add_lsoas_to_map(lsoas_in_radius,m,gdf_c,lsoa_population)

    avg_travel_time, population_covered=get_average_travel_times(origin,radius_metres,lsoa_population,G,lsoas_in_radius,speed)

    return m,avg_travel_time, population_covered
    


def get_average_travel_times(origin, radius_metres, lsoa_population, G,lsoas_in_radius,speed_mph):

    # calculate shortest paths from origin to LSOAs within search radius
    travel_times_secs = []
    weighted_traveltimes =[]
    weights=[]
    for lsoa_code in lsoas_in_radius:
        destination = (lsoa_population[lsoa_code]['Latitude'], lsoa_population[lsoa_code]['Longitude'])
        try:
            length_miles = nx.shortest_path_length(G, source=ox.distance.nearest_nodes(G, origin[1], origin[0]),
                                     target=ox.distance.nearest_nodes(G, destination[1], destination[0]), 
                                     weight='length')/1609.34
            
            travel_time_sec = (length_miles /speed_mph)*3600
            #sum([G[u][v][0]['travel_time'] for u, v in zip(route[:-1], route[1:])])
            travel_times_secs.append(travel_time_sec)
            weight=lsoa_population[lsoa_code]['Population']
            weighted_traveltimes.append(travel_time_sec*weight)
            weights.append(weight)

        except nx.NetworkXNoPath:
            pass

    # calculate average travel time and population within search radius
    avg_travel_time = sum(travel_times_secs) / len(travel_times_secs) / 60
    avg_weighted_travel_time = sum(weighted_traveltimes) / sum(weights) /60
    population_covered = sum([lsoa_population[lsoa]['Population'] for lsoa in lsoas_in_radius])


    return round(avg_weighted_travel_time), round(population_covered)




def add_lsoas_to_map(lsoas,m,gdf_c,lsoa_population):
    for lsoa_code in lsoas:
        row = gdf_c.loc[gdf_c['LSOA21CD'] == lsoa_code].iloc[0]
        population=lsoa_population[lsoa_code]['Population']

        if row['geometry'].geom_type == 'Polygon':
            lsoa_boundary = [tuple(reversed(coord)) for coord in list(row['geometry'].exterior.coords)]
        elif row['geometry'].geom_type == 'MultiPolygon':
            largest_polygon = max(row['geometry'], key=lambda x: x.area) 
            lsoa_boundary = [tuple(reversed(coord)) for coord in list(largest_polygon.exterior.coords)]

    

        lsoa_polygon = folium.Polygon(
            locations=lsoa_boundary,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.2,
            tooltip=str(population),
        )

   
        lsoa_polygon.add_to(m)

