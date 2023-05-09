import osmnx as ox
import networkx as nx
import folium
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import itertools
import math
from functions.tsp_functions import tsp, tsp_greedy, perm_or_greedy
import os
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations


def main(filtered_df, start_address, network_type, radius_miles):
    # county = filtered_df['County'].iloc[0] if filtered_df['County'].iloc[0] != 'N/A' else filtered_df['County'].iloc[1]
    ox.config(log_console=True, use_cache=True)
    # start_location = ox.geocode(start_address)
    # G = ox.graph_from_place(city_or_county, network_type=network_type)

    # target = ox.nearest_nodes(G, start_location[1],Y=start_location[0])
    geolocator = Nominatim(user_agent="myGeocoder")

    coords, addresses = get_coords_addresses(filtered_df, geolocator)
    north = max([lat for (lat, long) in coords]) + (
        0.01 * (radius_miles / 1.6)
    )  # about a km extra
    south = min([lat for (lat, long) in coords]) - (
        0.01 * (radius_miles / 1.6)
    )  # about a km extra
    east = max([long for (lat, long) in coords]) + (
        0.02 * (radius_miles / 1.6)
    )  # about a km extra
    west = min([long for (lat, long) in coords]) - (
        0.02 * (radius_miles / 1.6)
    )  # about a km extra

    G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
    # G = ox.graph_from_place(county, network_type=network_type)

    """
    use_long_lat = False
    if 'Longitude' in filtered_df.columns and 'Latitude' in filtered_df.columns:
        use_long_lat = True

    
    coords = []

    for _, row in filtered_df.iterrows():
        try:
            if use_long_lat:
                coord = (row['Latitude'], row['Longitude'])
            else:
                location = geolocator.geocode(row['Address'])
                coord = (location.latitude, location.longitude)
            coords.append(coord)
        except Exception as e:
            print(f"Error: {e}")
            pass

    # make addresses a list
    addresses=list(filtered_df['Address'])
    """
    # distance dict
    distance_dict = {}
    for coord_pair in combinations(coords, 2):
        coord1, coord2 = coord_pair
        if coord1 == coord2:
            distance = 0
        else:
            node1 = ox.distance.nearest_nodes(G, X=[coord1[1]], Y=[coord1[0]])[0]
            node2 = ox.distance.nearest_nodes(G, X=[coord2[1]], Y=[coord2[0]])[0]
            distance = nx.shortest_path_length(G, node1, node2, weight="length")
        distance_dict[(coord1, coord2)] = distance
        distance_dict[(coord2, coord1)] = distance

    shortest_route_addresses, shortest_route_coords, shortest_distance = tsp(
        coords, addresses, distance_dict, first_address=start_address
    )
    (
        shortest_route_addresses_g,
        shortest_route_coords_g,
        shortest_distance_g,
    ) = tsp_greedy(coords, addresses, distance_dict, first_address=start_address)

    shortest_route_addresse, shortest_route_coord = perm_or_greedy(
        G,
        shortest_route_addresses,
        shortest_route_coords,
        shortest_distance,
        shortest_route_addresses_g,
        shortest_route_coords_g,
        shortest_distance_g,
    )

    # Find the nearest nodes for each coordinate in the shortest route for tsp permutations
    nodes = [
        ox.distance.nearest_nodes(G, X=[coord[1]], Y=[coord[0]])[0]
        for coord in shortest_route_coord
    ]
    shortest_paths = [
        nx.shortest_path(G, nodes[i], nodes[i + 1], weight="length")
        for i in range(len(nodes) - 1)
    ]
    path_lengths = [
        nx.shortest_path_length(G, nodes[i], nodes[i + 1], weight="length") / 1609.34
        for i in range(len(nodes) - 1)
    ]

    # Create a map centreed on the first address in the shortest route
    map_centre = shortest_route_coord[1]
    m = folium.Map(location=map_centre, max_bounds=True)

    # Add markers for each address in the shortest route
    already_added_coords = set()
    for i, (address, coord) in enumerate(
        zip(shortest_route_addresse, shortest_route_coord)
    ):
        if coord in already_added_coords:
            continue
        already_added_coords.add(coord)
        tooltip = f"{i+1}. {address}"
        folium.Marker(location=coord, tooltip=tooltip).add_to(m)

    # Draw the shortest paths on the map
    for path in shortest_paths:
        route_nodes_coords = [G.nodes[node] for node in path]
        route_coords = [(node["y"], node["x"]) for node in route_nodes_coords]
        folium.PolyLine(route_coords, color="blue", weight=2.5).add_to(m)

    walking_speed = 3  # mph
    peak_driving_speed = 15  # mph
    off_peak_driving_speed = 25  # mph
    cycle_speed = 16  # mph

    distance_data = {
        "From": shortest_route_addresse[:-1],
        "To": shortest_route_addresse[1:],
        "Distance (miles)": [round(dist, 2) for dist in path_lengths],
        "Total Distance (miles)": [
            round(sum(path_lengths[: i + 1]), 2) for i in range(len(path_lengths))
        ],
        "Walking time (min)": [
            round(dist / walking_speed * 60, 0) for dist in path_lengths
        ],
        "Peak driving time (min)": [
            round(dist / peak_driving_speed * 60, 0) for dist in path_lengths
        ],
        "Off-peak driving time (min)": [
            round(dist / off_peak_driving_speed * 60, 0) for dist in path_lengths
        ],
        "Cycle time (min)": [
            round(dist / cycle_speed * 60, 0) for dist in path_lengths
        ],
    }
    df = pd.DataFrame(distance_data)
    return m, df

    """
    new_df = filtered_df[['Name', 'Address', 'Distance in Miles']].copy()
    new_df['Distance in Miles'] = new_df['Distance in Miles'].round(2)
    walking_speed = 3  # mph    
    new_df['Walking time (min)'] = (new_df['Distance in Miles'] / walking_speed) * 60


    peak_driving_speed = 15  # mph
    new_df['Peak driving time (min)'] = (new_df['Distance in Miles'] / peak_driving_speed) * 60


    off_peak_driving_speed = 25  # mph
    new_df['Off-peak driving time (min)'] = (new_df['Distance in Miles'] / off_peak_driving_speed) * 60

    cycle_speed = 16 #mph
    new_df['Cycle time (min)'] = (new_df['Distance in Miles'] / cycle_speed)* 60
    """


def get_coords_addresses(df, geolocator):
    use_long_lat = False
    if "Longitude" in df.columns and "Latitude" in df.columns:
        use_long_lat = True

    coords = []

    for _, row in df.iterrows():
        try:
            if use_long_lat:
                coord = (row["Latitude"], row["Longitude"])
            else:
                location = geolocator.geocode(row["Address"])
                coord = (location.latitude, location.longitude)
            coords.append(coord)
        except Exception as e:
            print(f"Error: {e}")
            pass

    # make addresses a list
    addresses = list(df["Address"])

    return coords, addresses
