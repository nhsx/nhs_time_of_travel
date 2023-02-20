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

def main(city_or_county,filtered_df,target_address,network_type):
    ox.config(log_console=True, use_cache=True)
    target_location = ox.geocode(target_address)
    G = ox.graph_from_place(city_or_county, network_type=network_type)
    target = ox.nearest_nodes(G, target_location[1],Y=target_location[0])

    coords = []
    for address in filtered_df['Address']:
        try:
            coords.append(ox.geocoder.geocode(address))
        except Exception as e:
            pass
    list=[]
    for i,c in enumerate(coords):
        list.append(ox.nearest_nodes(G,X=coords[i][1],Y=coords[i][0]))
    routes = []
    for i,a in enumerate(list):
        routes.append(nx.shortest_path(G,list[i],target,weight="length"))
    lengths=[]
    for i,b in enumerate(routes):
        lengths.append(nx.shortest_path_length(G,source=list[i],target=target,weight='length'))
    filtered_df['lengths'] = np.array(lengths)
    #Gx = ox.plot_graph_routes(G, routes, route_color='r', route_linewidth=6, bgcolor='k')
    #route_map = ox.plot_route_folium(G, routes[0], route_color = '#ff0000', opacity = 0.5)
    route_map = ox.plot_route_folium(G,routes[0])
    for route in routes:
            route_map = ox.plot_route_folium(G, route, route_map = route_map)
    iframe = folium.IFrame('<font face = "Arial"><b>{}</b> {}.</font>'.format(target_address,target_location))
    popup = folium.Popup(iframe, min_width=200, max_width=200)
    folium.Marker(location=target_location,popup = popup).add_to(route_map)

    filtered_df['lengths'] = np.array(lengths)



    return route_map, filtered_df
