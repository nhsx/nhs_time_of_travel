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
from scripts.mclp_functions2 import routes_to_featuregroup as routes_to_featuregroup

def main(city_or_county,filtered_df,target_address,network_type):
    ox.config(log_console=True, use_cache=True)
    target_location = ox.geocode(target_address)
    G = ox.graph_from_place(city_or_county, network_type=network_type)
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
            lengths.append(nx.shortest_path_length(G,source=nodes,target=target,weight='length'))
            names.append(row['Name'])

        except Exception as e:
            lengths.append(math.nan)
            pass

    # filtered_df['lengths'] = np.array(lengths)
    #Gx = ox.plot_graph_routes(G, routes, route_color='r', route_linewidth=6, bgcolor='k')
    #route_map = ox.plot_route_folium(G, routes[0], route_color = '#ff0000', opacity = 0.5)

    route_map = ox.plot_route_folium(G,routes[0])
    colors=['green', 'red', 'yellow', 'blue', 'pink', 'purple']
    for i, route in enumerate(routes):

        layer = routes_to_featuregroup(G, routes=[route], color=colors[i], name=names[i])
        layer.add_to(route_map)

    print('target', target_address,target_location)
    iframe = folium.IFrame('<font face = "Arial"><b>{}</b> {}.</font>'.format(target_address,target_location))
    popup = folium.Popup(iframe, min_width=200, max_width=200)
    folium.Marker(location=target_location,popup = popup).add_to(route_map)


    filtered_df['lengths'] = np.array(lengths)
    for i, (_,row) in enumerate(filtered_df.iterrows()):

        source_markers(row, route_map, color=colors[i])
        # print('color ' , _, i, row)

    folium.LayerControl().add_to(route_map)


    return route_map, filtered_df

def source_markers(row, route_map, color):
    target_loc = (row['Latitude'], row['Longitude'])
    iframe2 = folium.IFrame('<font face = "Arial"><b>{}</b> {}.</font>'.format(row['Name'],row['Address'],))
    popup2 = folium.Popup(iframe2, min_width=200, max_width=200, )
    folium.Marker(location=target_loc,popup = popup2, icon=folium.Icon(color=color)).add_to(route_map)
