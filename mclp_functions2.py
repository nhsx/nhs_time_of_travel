import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx
import osmnx as ox
import geopandas as gpd
import networkx as nx
from cartopy.geodesic import Geodesic
from shapely.geometry.polygon import Point, Polygon
from shapely.geometry import shape
from shapely.ops import unary_union
import nhstravel.loaders.lsoaloader as lsoaloader
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


#function to call lsoa loaders library to import lsoa data for the given regin
def load_lsoa(region):
    cambridge_lsoa_with_population_pd = lsoaloader.build_lsoa_data_frame_for_area_england("Cambridge")
    remapped_lsoa = lsoaloader.load_geo_json_shapefiles_for_lsoas(cambridge_lsoa_with_population_pd, "Cambridge")
    return remapped_lsoa

#genearte the collection of lsoas for each target location
def generate_neighboring_polys(remapped_lsoa, list_of_target_coords, radius):
    gd = Geodesic()

    list_of_neighboring_poly_dicts = []

    for target_coords in list_of_target_coords:
        target_point = Point(target_coords[1], target_coords[0])
        bounding_poly = Polygon(gd.circle(lon=target_coords[1], lat=target_coords[0], radius=radius))

        neighboring_polys = {'lsoa_codes':[], 'population':[], 'polygons':[]}
        for lsoa in remapped_lsoa['features']:
            lsoa_polygon = shape(lsoa['geometry'])
            if lsoa_polygon.contains(target_point) or bounding_poly.intersects(lsoa_polygon):
                neighboring_polys['lsoa_codes'].append(lsoa['properties']['LSOA21CD'])
                neighboring_polys['population'].append(lsoa['properties']['all ages'])
                neighboring_polys['polygons'].append(lsoa_polygon)

        list_of_neighboring_poly_dicts.append(neighboring_polys)

    return list_of_neighboring_poly_dicts

#funtion to generate the sample of nodes from each collection of lsoas for each target location
def generate_nodes_samples(list_of_neighboring_poly_dicts, list_of_target_nodes, nodes):
    list_of_nodes_samples = []
    for neighboring_polys, target_node in zip(list_of_neighboring_poly_dicts, list_of_target_nodes):
        nodes_sample = pd.DataFrame(columns = nodes.columns)
        list_of_lsoa_codes = []
        list_of_pops = []


        for i in range(len(neighboring_polys['polygons'])):
            lsoa = neighboring_polys['polygons'][i]
            for j in range(nodes.shape[0]):
                if lsoa.contains(nodes.iloc[j]['geometry']):
                    nodes_sample = nodes_sample.append(nodes.iloc[j])
                    list_of_lsoa_codes.append(neighboring_polys['lsoa_codes'][i])
                    list_of_pops.append(neighboring_polys['population'][i])

        nodes_sample['lsoa_codes'] = list_of_lsoa_codes
        nodes_sample['lsoa_population'] = list_of_pops

        nodes_sample = nodes_sample.drop(target_node)

        list_of_nodes_samples.append(nodes_sample)
    return list_of_nodes_samples


#creating a function to calculate a score from a list of lengths calculated from the target node to each of the 100 sample nodes
def create_score(list_of_lengths, list_of_multipliers):
    score = 1000
    for l, m in zip(list_of_lengths, list_of_multipliers):
        deduction = (((l/1000)/4.5)*60) * m * 5#get the length in km divide by speed 4.5 km/h then divide by 60 to get time in minutes
        score = score - deduction #decrement the score by the derivation of time taken to each of the 100 nodes
        return score

#define a function to calculate multiple shortest route lengths from the target node to each of the 100 sample nodes
def create_list_of_lengths(G, nodes_sample, target_node):
    list_of_lengths = []
    list_of_multipliers = []
    for node in nodes_sample.index:
        total_pop = nodes_sample['lsoa_population'].unique().sum()
        node_pop = nodes_sample['lsoa_population'][node]
        multiplier = 1 - (node_pop/total_pop)
        length = nx.shortest_path_length(G, source=node, target=target_node, weight='length') #calculate route from target node to sample node
        list_of_lengths.append(length) #append the length to the list
        list_of_multipliers.append(multiplier) #append the multipliers to the list for score creation
    
    return [list_of_lengths, list_of_multipliers]

#function to generate the score for each of the potential target sites provided using create_score()
def generate_target_scores(G, list_of_nodes_samples, list_of_target_nodes, list_of_target_addresses):
    target_scores = {}
    site_names = []
    for i in range(len(list_of_target_nodes)):
        nodes_sample = list_of_nodes_samples[i]
        site_name = 'Site {}'.format(i + 1)
        site_address = list_of_target_addresses[i]
        target_lengths = create_list_of_lengths(G, nodes_sample, list_of_target_nodes[i])
        target_scores[site_name] = create_score(target_lengths[0], target_lengths[1])
        print('The score for {}: {} is {}'.format(site_name, site_address, target_scores[site_name]))
        site_names.append(site_name)
    return site_names, target_scores

#fucntion to generate the multiple shortest routes from the target node to each of the sample nodes
def generate_msr(G, site_names, list_of_target_nodes, list_of_nodes_samples):
    target_to_node_routes = {}
    for site, target_node, nodes_sample in zip(site_names, list_of_target_nodes, list_of_nodes_samples):
        list_of_routes = []
        for node in nodes_sample.index:
            route = nx.shortest_path(G, source=node, target=target_node, weight='length') #calculate route from target node to sample node
            list_of_routes.append(route) #append the length to the list
        target_to_node_routes[site] = list_of_routes
    return target_to_node_routes

#function to plot each of the routes from the target node to the sample nodes as a folium map and add a marker for the target node
#save each of the folium maps as a folium object in the list route_maps to be displayed by streamlit
def generate_route_maps(G, target_to_node_routes, site_names, list_of_target_addresses, list_of_target_coords, target_scores):
    route_maps = []
    for site, target_address, target_coords in zip(site_names, list_of_target_addresses, list_of_target_coords):
        route_map = ox.plot_route_folium(G, target_to_node_routes[site][0], route_color = '#ff0000', opacity = 0.5)
        for route in target_to_node_routes[site][1:len(target_to_node_routes[site])]:
            route_map = ox.plot_route_folium(G, route, route_map = route_map, route_color = '#ff0000', opacity = 0.5)
        iframe = folium.IFrame('<font face = "Arial"><b>{}:</b> {}. <br><br><b>{} Score:</b> {}</br></br></font>'.format(site, target_address, site, target_scores[site]))
        popup = folium.Popup(iframe, min_width=200, max_width=300)
        folium.Marker(location=target_coords,
                    popup = popup).add_to(route_map)
        route_maps.append(route_map)
    return route_maps

#save each of the folium maps as a folium object in the list route_maps to be displayed by streamlit
def save_maps(site_names, route_maps):
    for site_name, map in zip(site_names, route_maps):
        map.save('route map for {}.html'.format(site_name))

#main function to generate networkx map then generate the scores and folium map for each proposed target location
def mclp_main(region, list_of_target_addresses):
    G, nodes = generate_networkx(region, 'walk')
    list_of_target_nodes, list_of_target_coords = get_target_nodes(G, list_of_target_addresses)

    cambridge_lsoa_with_population_pd = lsoaloader.build_lsoa_data_frame_for_area_england("Cambridge")
    remapped_lsoa = lsoaloader.load_geo_json_shapefiles_for_lsoas(cambridge_lsoa_with_population_pd, "Cambridge")

    #remapped_lsoa = load_lsoa(region)
    list_of_neighboring_poly_dicts = generate_neighboring_polys(remapped_lsoa, list_of_target_coords, radius)
    list_of_nodes_samples = generate_nodes_samples(list_of_neighboring_poly_dicts, list_of_target_nodes, nodes)
    site_names, target_scores = generate_target_scores(G, list_of_nodes_samples, list_of_target_nodes, list_of_target_addresses)
    #target_to_node_routes = generate_msr(G, site_names, list_of_target_nodes, list_of_nodes_samples)
    #route_maps = generate_route_maps(G, target_to_node_routes, site_names, list_of_target_addresses, list_of_target_coords, target_scores)
    #save_maps(site_names, route_maps)

    return target_scores#, route_maps

region = "Cambridge"
list_of_target_addresses = ["PAPWORTH ROAD, Cambridge", "4 TRUMPINGTON ROAD, Cambridge"]
radius = 500

mclp_main(region, list_of_target_addresses)
