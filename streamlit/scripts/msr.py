import streamlit as st
import pandas as pd
import warnings
import numpy as np
import os

os.environ["USE_PYGEOS"] = "0"
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


def main(filtered_df, target_address, network_type):
    ox.config(log_console=True, use_cache=True)
    target_location = ox.geocode(target_address)

    if "Longitude" in filtered_df.columns and "Latitude" in filtered_df.columns:
        pass

    else:
        filtered_df[["Latitude", "Longitude"]] = filtered_df.apply(
            lambda row: make_coords(row["Address"]), axis=1, result_type="expand"
        )
    print(filtered_df)
    coords = filtered_df.apply(
        lambda row: (row["Latitude"], row["Longitude"]), axis=1
    ).to_list()
    coords.append(target_location)

    north = max([lat for (lat, long) in coords]) + (0.01)  # about a km extra
    south = min([lat for (lat, long) in coords]) - (0.01)  # about a km extra
    east = max([long for (lat, long) in coords]) + (0.02)  # about a km extra
    west = min([long for (lat, long) in coords]) - (0.02)  # about a km extra

    G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
    target = ox.nearest_nodes(G, target_location[1], Y=target_location[0])

    routes = []
    distances_miles = []
    names = []
    for _, row in filtered_df.iterrows():
        try:
            coords = (row["Latitude"], row["Longitude"])

            nodes = ox.nearest_nodes(G, X=coords[1], Y=coords[0])
            routes.append(nx.shortest_path(G, nodes, target, weight="length"))
            distances_miles.append(
                nx.shortest_path_length(G, source=nodes, target=target, weight="length")
                / 1609.34
            )
            names.append(row["Name"])

        except Exception as e:
            distances_miles.append(math.nan)
            pass

    route_map = ox.plot_route_folium(G, routes[0])
    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "white",
        "pink",
        "lightblue",
        "lightgreen",
        "gray",
        "black",
        "lightgray",
    ]
    num_colors = len(colors)
    for i, route in enumerate(routes):
        color = colors[i % num_colors]
        layer = routes_to_featuregroup(G, routes=[route], color=color, name=names[i])
        layer.add_to(route_map)

    print("target", target_address, target_location)
    iframe = folium.IFrame(
        '<font face = "Arial"><b>{}</b> {}.</font>'.format(
            target_address, target_location
        )
    )
    popup = folium.Popup(iframe, min_width=200, max_width=200)
    folium.Marker(location=target_location, popup=popup).add_to(route_map)

    new_df = travel_times(filtered_df, distances_miles)

    for i, (_, row) in enumerate(filtered_df.iterrows()):
        color = colors[i % num_colors]
        source_markers(row, route_map, color=color)
        # print('color ' , _, i, row)

    folium.LayerControl().add_to(route_map)

    return route_map, new_df


def travel_times(filtered_df, distances_miles):
    """Calculates new dataframe with travel times by different nodes
    Inputs:
        filtered_df: a dataframe with columns Name, Address
        distances_miles: a sequence of distances in miles
    Returns:
        a new df with columns Name, Address, Distance in Miles, Walking time (min), Peak driving time (min), Off-peak driving time (min)
    """
    filtered_df["Distance in Miles"] = np.array(distances_miles)
    new_df = filtered_df[["Name", "Address", "Distance in Miles"]].copy()
    new_df["Distance in Miles"] = new_df["Distance in Miles"].round(2)
    walking_speed = 3  # mph
    new_df["Walking time (min)"] = (new_df["Distance in Miles"] / walking_speed) * 60

    peak_driving_speed = 15  # mph
    new_df["Peak driving time (min)"] = (
        new_df["Distance in Miles"] / peak_driving_speed
    ) * 60

    off_peak_driving_speed = 25  # mph
    new_df["Off-peak driving time (min)"] = (
        new_df["Distance in Miles"] / off_peak_driving_speed
    ) * 60
    return new_df


def get_lat_long(use_long_lat, row):
    if use_long_lat:
        coords = (row["Latitude"], row["Longitude"])
    else:
        coords = ox.geocoder.geocode(row["Address"])
    return coords


def make_coords(address):
    coords = ox.geocoder.geocode(address)
    if coords is None:
        return {"Latitude": None, "Longitude": None}
    else:
        return {"Latitude": coords[0], "Longitude": coords[1]}
