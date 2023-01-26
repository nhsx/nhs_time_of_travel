import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx
import osmnx as ox
import geopandas as gpd
import networkx as nx
import folium

#generate network x map of a specified region of a specific travel type (walk, drive e.tc)
def generate_networkx(region, type):
    G = ox.graph.graph_from_place(region, simplify = True, network_type = type)
    nodes, edges = ox.graph_to_gdfs(G)
    return G, nodes

#function to get osmid (node ids) for the potential target addresses given by the user
def get_target_nodes(G, list_of_target_addresses):
    list_of_target_nodes = []
    list_of_target_coords = []
    for target_address in list_of_target_addresses:
        target_coords = ox.geocode(target_address)
        target_node = ox.get_nearest_node(G, target_coords)
        list_of_target_nodes.append(target_node)
        list_of_target_coords.append(target_coords)
    return list_of_target_nodes, list_of_target_coords

#function to generate the random sample of n sample ndoes by first removing the target node location from the dataframe
def sample_nodes(nodes, list_of_target_nodes, n):
    #n can be specified to be a percentage of population, for now it is manually defined arbitrarily as 100
    nodes_df = nodes.copy()
    nodes_df = nodes_df[~nodes_df.index.isin(list_of_target_nodes)] #get the dataframe of nodes that do not have any target nodes in them
    nodes_sample = nodes_df[['y', 'x']].sample(n = n, random_state = 1234)
    return nodes_sample


#creating a function to calculate a score from a list of lengths calculated from the target node to each of the 100 sample nodes
def create_score(list_of_lengths):
    score = 1000
    for l in list_of_lengths:
        deduction = (((l/1000)/4.5)*60) * 5 #get the length in km divide by speed 4.5 km/h then divide by 60 to get time in minutes
        score = score - deduction #decrement the score by the derivation of time taken to each of the 100 nodes
        return score


#define a function to calculate multiple shortest route lengths from the target node to each of the 100 sample nodes
def create_list_of_lengths(G, nodes_sample, target_node):
    list_of_lengths = []
    for node in nodes_sample.index:
        length = nx.shortest_path_length(G, source=node, target=target_node, weight='length') #calculate route from target node to sample node
        list_of_lengths.append(length) #append the length to the list
    
    return list_of_lengths

#function to generate the score for each of the potential target sites provided using create_score()
def generate_target_scores(G, nodes_sample, list_of_target_nodes, list_of_target_addresses):
    target_scores = {}
    site_names = []
    for i in range(len(list_of_target_nodes)):
        site_name = 'Site {}'.format(i + 1)
        site_address = list_of_target_addresses[i]
        target_scores[site_name] = create_score(create_list_of_lengths(G, nodes_sample, list_of_target_nodes[i]))
        print('The score for {}: {} is {}'.format(site_name, site_address, target_scores[site_name]))
        site_names.append(site_name)
    return site_names, target_scores

#fucntion to generate the multiple shortest routes from the target node to each of the sample nodes
def generate_msr(G, site_names, list_of_target_nodes, nodes_sample):
    target_to_node_routes = {}
    for site, target_node in zip(site_names, list_of_target_nodes):
        list_of_routes = []
        for node in nodes_sample.index:
            route = nx.shortest_path(G, source=node, target=target_node, weight='length') #calculate route from target node to sample node
            list_of_routes.append(route) #append the length to the list
        target_to_node_routes[site] = list_of_routes
    return target_to_node_routes

#function to plot each of the routes from the target node to the sample nodes as a folium map and add a marker for the target node
#save each of the folium maps as a folium object in the list route_maps to be displayed by streamlit
def generate_route_maps(G, target_to_node_routes, site_names, list_of_target_addresses, list_of_target_coords):
    route_maps = []
    for site, target_address, target_coords in zip(site_names, list_of_target_addresses, list_of_target_coords):
        route_map = ox.plot_route_folium(G, target_to_node_routes[site][0], route_color = '#ff0000', opacity = 0.5)
        for route in target_to_node_routes[site][1:len(target_to_node_routes[site])]:
            route_map = ox.plot_route_folium(G, route, route_map = route_map, route_color = '#ff0000', opacity = 0.5)
        iframe = folium.IFrame('{}: {}'.format(site, target_address))
        popup = folium.Popup(iframe, min_width=200, max_width=200)
        folium.Marker(location=target_coords,
                    popup = popup).add_to(route_map)
        route_maps.append(route_map)
    return route_maps

#temporary function to test the maps generated above
def save_maps(site_names, route_maps):
    for site_name, map in zip(site_names, route_maps):
        map.save('route map for {}.html'.format(site_name))

#main function to generate networkx map then generate the scores and folium map for each proposed target location
def mclp_main(region, list_of_target_addresses):
    G, nodes = generate_networkx(region, 'walk')
    list_of_target_nodes, list_of_target_coords = get_target_nodes(G, list_of_target_addresses)
    nodes_sample = sample_nodes(nodes, list_of_target_nodes, 100)
    site_names, target_scores = generate_target_scores(G, nodes_sample, list_of_target_nodes, list_of_target_addresses)
    target_to_node_routes = generate_msr(G, site_names, list_of_target_nodes, nodes_sample)
    route_maps = generate_route_maps(G, target_to_node_routes, site_names, list_of_target_addresses, list_of_target_coords)
    save_maps(site_names, route_maps)

#region = "Cambridge"
#list_of_target_addresses = ["PAPWORTH ROAD, Cambridge", "4 TRUMPINGTON ROAD, Cambridge"]

#mclp_main(region, list_of_target_addresses)
