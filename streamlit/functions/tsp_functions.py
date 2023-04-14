
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
import itertools


def manhattan_distance(city1, city2):
    # Calculates the Manhattan distance between two cities
    x1, y1 = city1
    x2, y2 = city2
    return abs(x1 - x2) + abs(y1 - y2)

def tsp(cities, addresses):
   # Calculates the shortest possible route that visits all cities and returns to the starting city
   shortest_distance = float('inf')
   shortest_route = None
   address = addresses['Address']
   address_list = address.tolist()

   city_to_address = dict(zip(cities, address_list))
   print('city_to_address = ' , city_to_address)
   for route in itertools.permutations(cities):
       route_distance = 0
       for i in range(len(route)):
           if i == len(route) - 1:
               route_distance += manhattan_distance(route[i], route[0])
           else:
               route_distance += manhattan_distance(route[i], route[i+1])
       if route_distance < shortest_distance:
           shortest_distance = route_distance
           shortest_route = route
   shortest_route_addresses = [city_to_address[city] for city in shortest_route]
   print('tsp file shortest_route_addresses = ', shortest_route_addresses)
   return shortest_route_addresses, shortest_distance