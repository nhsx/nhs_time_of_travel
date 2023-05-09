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
import itertools


# tsp permutations code


def tsp(coords, addresses, distance_dict, first_address=None):
    shortest_distance = float("inf")
    shortest_route = None
    coord_to_address = dict(zip(coords, addresses))

    if first_address:
        if first_address not in addresses:
            raise ValueError(
                "The specified first_address is not in the list of addresses."
            )
        first_coord = list(coord_to_address.keys())[
            list(coord_to_address.values()).index(first_address)
        ]
        coords_copy = coords.copy()
        coords_copy.remove(first_coord)
        permutations = (
            tuple([first_coord] + list(route))
            for route in itertools.permutations(coords_copy)
        )
    else:
        permutations = itertools.permutations(coords)

    for route in permutations:
        route_distance = 0
        for i in range(len(route)):
            if i == len(route) - 1:
                route_distance += distance_dict[(route[i], route[0])]
            else:
                route_distance += distance_dict[(route[i], route[i + 1])]
        if route_distance < shortest_distance:
            shortest_distance = route_distance
            shortest_route = route

    shortest_route_addresses = [coord_to_address[coord] for coord in shortest_route]
    shortest_route_coords = [coord for coord in shortest_route]

    return shortest_route_addresses, shortest_route_coords, shortest_distance


# greedy algorithm code


def tsp_greedy(coords, addresses, distance_dict, first_address=None):
    if first_address:
        first_coord = coords[addresses.index(first_address)]
    else:
        first_coord = coords[0]
        first_address = addresses[0]

    remaining_coords = [coord for coord in coords if coord != first_coord]
    remaining_addresses = [address for address in addresses if address != first_address]

    shortest_route_coords_g = [first_coord]
    shortest_route_addresses_g = [first_address]
    shortest_distance_g = 0

    while remaining_coords:
        current_coord = shortest_route_coords_g[-1]
        min_distance = float("inf")
        next_coord = None
        next_address = None

        for coord, address in zip(remaining_coords, remaining_addresses):
            distance = distance_dict[(current_coord, coord)]
            if distance < min_distance:
                min_distance = distance
                next_coord = coord
                next_address = address

        shortest_route_coords_g.append(next_coord)
        shortest_route_addresses_g.append(next_address)
        shortest_distance_g += min_distance
        remaining_coords.remove(next_coord)
        remaining_addresses.remove(next_address)

    return shortest_route_addresses_g, shortest_route_coords_g, shortest_distance_g


# compare the results and pick the shortest route from the two lengths.


def perm_or_greedy(
    G,
    shortest_route_addresses,
    shortest_route_coords,
    shortest_distance,
    shortest_route_addresses_g,
    shortest_route_coords_g,
    shortest_distance_g,
):
    # Find the nearest nodes for each coordinate in the shortest route
    nodes = [
        ox.distance.nearest_nodes(G, X=[coord[1]], Y=[coord[0]])[0]
        for coord in shortest_route_coords
    ]
    shortest_paths = [
        nx.shortest_path(G, nodes[i], nodes[i + 1], weight="length")
        for i in range(len(nodes) - 1)
    ]
    path_lengths = [
        nx.shortest_path_length(G, nodes[i], nodes[i + 1], weight="length") / 1609.34
        for i in range(len(nodes) - 1)
    ]

    # doing the tsp_greedy conversion to nodes and network distance
    nodes_g = [
        ox.distance.nearest_nodes(G, X=[coord[1]], Y=[coord[0]])[0]
        for coord in shortest_route_coords_g
    ]
    shortest_paths_g = [
        nx.shortest_path(G, nodes_g[i], nodes_g[i + 1], weight="length")
        for i in range(len(nodes_g) - 1)
    ]
    path_lengths_g = [
        nx.shortest_path_length(G, nodes_g[i], nodes_g[i + 1], weight="length")
        / 1609.34
        for i in range(len(nodes_g) - 1)
    ]

    # Find the shortest path
    if sum(path_lengths) < sum(path_lengths_g):
        shortest_paths = shortest_paths
        shortest_route_addresse = shortest_route_addresses
        shortest_route_coord = shortest_route_coords
    else:
        shortest_paths = shortest_paths_g
        shortest_route_addresse = shortest_route_addresses_g
        shortest_route_coord = shortest_route_coords_g

    return shortest_route_addresse, shortest_route_coord
