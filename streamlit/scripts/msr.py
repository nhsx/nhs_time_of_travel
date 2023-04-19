import streamlit as st
import pandas as pd
import warnings
import numpy as np
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx
import osmnx as ox
import geopandas as gpd
import folium
import math
from scripts.msr_functions import routes_to_featuregroup as routes_to_featuregroup
from scripts.msr_functions import source_markers

def main(city_or_county,filtered_df,target_address,network_type):
    county = filtered_df['County'].iloc[0] if filtered_df['County'].iloc[0] != 'N/A' else filtered_df['County'].iloc[1]

    ox.config(log_console=True, use_cache=True)
    target_location = ox.geocode(target_address)
    G = ox.graph_from_place(county, network_type=network_type)
    target = ox.nearest_nodes(G, target_location[1],Y=target_location[0])

    use_long_lat = False
    if 'Longitude' in filtered_df.columns and 'Latitude' in filtered_df.columns:
        use_long_lat = True

    routes = []
    lengths=[]
    names=[]
    for _,row in filtered_df.iterrows():
        try:
            if use_long_lat:
                coords = (row['Latitude'], row['Longitude'])
            else:
                coords = ox.geocoder.geocode(row['Address'])

            nodes = ox.nearest_nodes(G,X=coords[1],Y=coords[0])
            routes.append(nx.shortest_path(G,nodes,target,weight="length"))
            lengths.append(nx.shortest_path_length(G,source=nodes,target=target,weight='length')/1609.34)
            names.append(row['Name'])

        except Exception as e:
            lengths.append(math.nan)
            pass

    # filtered_df['lengths'] = np.array(lengths)
    #Gx = ox.plot_graph_routes(G, routes, route_color='r', route_linewidth=6, bgcolor='k')
    #route_map = ox.plot_route_folium(G, routes[0], route_color = '#ff0000', opacity = 0.5)

    route_map = ox.plot_route_folium(G,routes[0])
    colors=['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    num_colors = len(colors)
    for i, route in enumerate(routes):
        color = colors[i % num_colors]
        layer = routes_to_featuregroup(G, routes=[route], color=color, name=names[i])
        layer.add_to(route_map)

    print('target', target_address,target_location)
    iframe = folium.IFrame('<font face = "Arial"><b>{}</b> {}.</font>'.format(target_address,target_location))
    popup = folium.Popup(iframe, min_width=200, max_width=200)
    folium.Marker(location=target_location,popup = popup).add_to(route_map)


    filtered_df['Distance in Miles'] = np.array(lengths)
    new_df = filtered_df[['Name', 'Address', 'Distance in Miles']].copy()
    new_df['Distance in Miles'] = new_df['Distance in Miles'].round(2)
    walking_speed = 3  # mph    
    new_df['Walking time (min)'] = (new_df['Distance in miles'] / walking_speed) * 60


    peak_driving_speed = 15  # mph
    new_df['Peak driving time (min)'] = (new_df['Distance in miles'] / peak_driving_speed) * 60


    off_peak_driving_speed = 25  # mph
    new_df['Off-peak driving time (min)'] = (new_df['Distance in miles'] / off_peak_driving_speed) * 60

    
    for i, (_,row) in enumerate(filtered_df.iterrows()):
        color = colors[i % num_colors]
        source_markers(row, route_map, color=color)
        # print('color ' , _, i, row)

    folium.LayerControl().add_to(route_map)


    return route_map, new_df

