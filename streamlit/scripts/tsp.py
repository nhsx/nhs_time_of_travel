import osmnx as ox
import networkx as nx
import folium
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import itertools
import math
from scripts.mclp_functions2 import routes_to_featuregroup as routes_to_featuregroup
from functions.tsp_functions import manhattan_distance, tsp
import os
import pandas as pd
import matplotlib.pyplot as plt




def main(city_or_county,filtered_df,start_address,network_type):
    ox.config(log_console=True, use_cache=True)
    start_location = ox.geocode(start_address)
    G = ox.graph_from_place(city_or_county, network_type=network_type)
    target = ox.nearest_nodes(G, start_location[1],Y=start_location[0])
    geolocator = Nominatim(user_agent="myGeocoder")


    use_long_lat = False
    if 'Longitude' in filtered_df.columns and 'Latitude' in filtered_df.columns:
        use_long_lat = True

    
    locations = []
    for _,row in filtered_df.iterrows():
        try:
            if use_long_lat:
                coords = (row['Latitude'], row['Longitude'])
            else:
                coords = ox.geocoder.geocode(row['Address'])
        
        except Exception as e:
            pass


    shortest_route_addresses, shortest_distance = tsp(locations, filtered_df)


    


    # Create a map centered on the first address in the shortest route
    #map_centre = locations[0]
    m = folium.Map(location=ox.geocode(city_or_county), zoom_start=13)


    for i, address in enumerate(shortest_route_addresses):
        location = geolocator.geocode(address)
        if location is not None:
               lat, lon = location.latitude, location.longitude
               tooltip = f"{i+1}. {address}"
               folium.Marker(location=[lat, lon], tooltip=tooltip).add_to(m)
        else:
            print(f"Could not find location for address: {address}")
    locations_ordered = []
    for address in shortest_route_addresses:
        location = geolocator.geocode(address)
        if location is not None:
            lat, lon = location.latitude, location.longitude
            locations_ordered.append((lat, lon))
        else:
            print(f"Could not find location for address: {address}")
    nodes = [ox.distance.nearest_nodes(G, X=[coord[1]], Y=[coord[0]])[0] for coord in locations_ordered]
    shortest_paths = [nx.shortest_path(G, nodes[i], nodes[i + 1], weight='length') for i in range(len(nodes) - 1)]
    path_lengths = [nx.shortest_path_length(G, nodes[i], nodes[i + 1], weight='length')/1609.34 for i in range(len(nodes) - 1)]
    for path in shortest_paths:
        route_nodes_coords = [G.nodes[node] for node in path]
        route_coords = [(node['y'], node['x']) for node in route_nodes_coords]
        folium.PolyLine(route_coords, color='blue', weight=2.5).add_to(m)
    distance_data = {
    'From': shortest_route_addresses[:-1],
    'To': shortest_route_addresses[1:],
    'Distance (miles)': [round(dist,2) for dist in path_lengths],
    'Cumulative Distance (miles)': [round(sum(path_lengths[:i+1]),2) for i in range(len(path_lengths))]
}  
    df = pd.DataFrame(distance_data)

    return m, df

