import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx
import osmnx as ox
import geopandas as gpd
import networkx as nx
import folium
import streamlit as st


def routes_to_featuregroup(G, routes, color, name):
    """
    Convert a networkx route into a folium FeatureGroup

    Args:
        G: Networkx graph of area
        routes: list of routes, each of which is a list of node indices
        color: color for lines in folium
        name: name for resulting feature group

    Returns:
        a feature group with all routes as lines
    """
    layer = folium.FeatureGroup(name=name)
    lines = []
    if routes:
        for route in routes:
            route_coords = []
            for node in route:
                route_coords.append((G.nodes[node]["y"], G.nodes[node]["x"]))
            lines.append(route_coords)
    folium.PolyLine(lines, color=color, weight=2, opacity=0.5).add_to(layer)

    return layer


def source_markers(row, route_map, color):
    target_loc = (row["Latitude"], row["Longitude"])
    iframe2 = folium.IFrame(
        '<font face = "Arial"><b>{}</b> {}.</font>'.format(
            row["Name"],
            row["Address"],
        )
    )
    popup2 = folium.Popup(iframe2, min_width=200, max_width=200)
    folium.Marker(
        location=target_loc, popup=popup2, icon=folium.Icon(color=color)
    ).add_to(route_map)
