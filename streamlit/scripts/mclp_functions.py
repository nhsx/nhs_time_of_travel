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
import streamlit as st


# use the postcode lookup csv to get the lsoa regions for each target location to pass to the lsoa loaders function
def get_lsoas_from_postcode(list_of_target_addresses):
    postcode_lookup = pd.read_csv(
        "data/PCD_OA21_LSOA21_MSOA21_LAD_NOV22_UK_LU 3.csv", encoding="ISO-8859-1"
    )
    # get the lsoa 2021 code from the lookup file
    lsoa_names = []
    # lsoa_codes = []
    for postcode in list_of_target_addresses:
        # lsoa_codes.append(postcode_lookup.loc[postcode_lookup['pcds'] == postcode]['lsoa21cd'].values[0])
        lsoa_names.append(
            postcode_lookup.loc[postcode_lookup["pcds"] == postcode]["ladnm"].values[0]
        )
    return lsoa_names


# function to call lsoa loaders library to import lsoa data for the given regin
def load_lsoa(region):
    print("building lsoa for ", region)
    remapped_lsoas_dict = {}
    lsoa_with_population_pd = lsoaloader.build_lsoa_data_frame_for_area_england(region)
    remapped_lsoa = lsoaloader.load_geo_json_shapefiles_for_lsoas(
        lsoa_with_population_pd, region
    )
    remapped_lsoas_dict[region] = remapped_lsoa
    return remapped_lsoa, remapped_lsoas_dict


# for each lsoa region use the lsoa loaders function to load in the data from that region
# create a dictionary of polygons containing all neighbouring polygons within the user specified radius
def generate_neighboring_polys(list_of_target_addresses, lsoa_names, radius):
    neighboring_polys_dict = {}
    for address, lsoa_region in zip(list_of_target_addresses, lsoa_names):
        # load in lsoa data using the loaders function in nhs travel
        remapped_lsoa, remapped_lsoas_dict = load_lsoa(lsoa_region)

        # convert the postcode to lat long coordinates
        target_coords = ox.geocode(address)

        # create the bounding poly from target location of size = radius specified
        gd = Geodesic()
        bounding_poly = Polygon(
            gd.circle(lon=target_coords[1], lat=target_coords[0], radius=radius)
        )

        # convert coordinates to a point object to check if this point is contained within the bounding poly
        target_point = Point(target_coords[1], target_coords[0])

        # store the features from remapped_lsoa (lsoa_loaders module)
        neighboring_polys = {"lsoa_codes": [], "population": [], "polygons": []}
        for lsoa in remapped_lsoa["features"]:
            lsoa_polygon = shape(lsoa["geometry"])
            if lsoa_polygon.contains(target_point) or bounding_poly.intersects(
                lsoa_polygon
            ):
                neighboring_polys["lsoa_codes"].append(lsoa["properties"]["LSOA21CD"])
                neighboring_polys["population"].append(lsoa["properties"]["all ages"])
                neighboring_polys["polygons"].append(lsoa_polygon)

        neighboring_polys_dict[address] = neighboring_polys
    return neighboring_polys_dict, remapped_lsoas_dict


# create networkx map from the neighbouring polygons we create using the function above
# without allow_output_mutation, st.cache is performing a hash of the entire graph on every run. This is taking a long time. Skip check
@st.cache(persist=True, allow_output_mutation=True)
def generate_networkx(list_of_target_addresses, neighboring_polys_dict, type):
    # intiialise main dict to contain each networkx map and nodes
    networkx_dict = {}

    for address in list_of_target_addresses:
        # initialies data types for each address in the dictionary
        networkx_dict[address] = {}

        # create merged polygon to generate map from this area
        merged_poly = unary_union(neighboring_polys_dict[address]["polygons"])

        # generate networkx map and nodes and store in dictionary under the sub key for address
        G = ox.graph_from_polygon(merged_poly)
        networkx_dict[address]["map"] = G
        nodes, edges = ox.graph_to_gdfs(G)
        networkx_dict[address]["nodes"] = nodes

    return networkx_dict


# funtion to generate the sample of nodes from each collection of lsoas for each target location
def generate_nodes_samples(
    list_of_target_adddresses, neighboring_poly_dict, networkx_dict
):
    dict_of_nodes_samples = {}
    for address in list_of_target_addresses:
        nodes = networkx_dict[address]["nodes"]
        nodes_sample = pd.DataFrame(columns=nodes.columns)
        neighboring_polys = neighboring_polys_dict[address]

        target_coords = ox.geocode(address)
        target_node = ox.get_nearest_node(networkx_dict[address]["map"], target_coords)

        list_of_lsoa_codes = []
        list_of_pops = []

        for i in range(len(neighboring_polys["polygons"])):
            lsoa = neighboring_polys["polygons"][i]
            for j in range(nodes.shape[0]):
                if lsoa.contains(nodes.iloc[j]["geometry"]):
                    nodes_sample = nodes_sample.append(nodes.iloc[j])
                    list_of_lsoa_codes.append(neighboring_polys["lsoa_codes"][i])
                    list_of_pops.append(neighboring_polys["population"][i])

        nodes_sample["lsoa_codes"] = list_of_lsoa_codes
        nodes_sample["lsoa_population"] = list_of_pops

        nodes_sample = nodes_sample.drop(target_node)

        dict_of_nodes_samples[address] = nodes_sample
    return dict_of_nodes_samples


# creating a function to calculate a score from a list of lengths calculated from the target node to each of the 100 sample nodes
def create_score(list_of_lengths, list_of_pop_fracs, list_of_node_pops):
    average_walk = 0
    for l, m in zip(list_of_lengths, list_of_pop_fracs):
        distance_km = l / 1000
        time_hours = distance_km / 4.5
        time_minutes = time_hours * 60
        time_increment = (
            time_minutes * m
        )  # get the length in km divide by speed 4.5 km/h then divide by 60 to get time in minutes
        average_walk = (
            average_walk + time_increment
        )  # decrement the score by the derivation of time taken to each of the 100 nodes

    total_pop = sum(list_of_node_pops)
    return average_walk, total_pop


# define a function to calculate multiple shortest route lengths from the target node to each of the 100 sample nodes
def create_list_of_lengths(G, nodes_sample, target_node):
    list_of_lengths = []
    list_of_pop_fracs = []
    list_of_node_pops = []

    for node in nodes_sample.index:
        current_lsoa = nodes_sample["lsoa_codes"][node]
        nodes_in_lsoa = nodes_sample.loc[
            nodes_sample["lsoa_codes"] == current_lsoa
        ].shape[0]
        total_pop = nodes_sample["lsoa_population"].unique().sum()
        node_pop = nodes_sample["lsoa_population"][node] / nodes_in_lsoa
        list_of_node_pops.append(node_pop)
        pop_fraction = node_pop / total_pop

        try:
            length = nx.shortest_path_length(
                G, source=node, target=target_node, weight="length"
            )  # calculate route from target node to sample node
        except Exception as e:
            pass
        list_of_lengths.append(length)  # append the length to the list
        list_of_pop_fracs.append(
            pop_fraction
        )  # append the multipliers to the list for score creation

    return [list_of_lengths, list_of_pop_fracs, list_of_node_pops]


# function to generate the score for each of the potential target sites provided using create_score()
def generate_target_routes_and_scores(
    networkx_dict, dict_of_nodes_samples, list_of_target_addresses, radius
):
    target_scores = {}
    site_names = []
    target_to_node_routes = {}
    i = 1

    for address in list_of_target_addresses:
        # initialise all variables
        list_of_routes = []
        # retrieve node sample using address lookup
        nodes_sample = dict_of_nodes_samples[address]
        # create site name for each postcode
        site_name = "Site {}".format(i)
        # retrieve networkx map from dict using address lookup
        G = networkx_dict[address]["map"]

        # convert post code to lat long and use this to find the nearest node on the network x
        target_coords = ox.geocode(address)
        target_node = ox.get_nearest_node(G, target_coords)

        # call our create_list_of_lengths and create_score functions defined above to generate the scores for each target site
        target_lengths = create_list_of_lengths(G, nodes_sample, target_node)
        target_scores[site_name] = create_score(
            target_lengths[0], target_lengths[1], target_lengths[2]
        )
        print(
            "{} at {} has an average walk time of: %.2f minutes in a radius of {} metres".format(
                site_name, address, radius
            )
            % target_scores[site_name][0]
        )
        print(
            "{} at {} has an average population score of: %.2f in a radius of {} metres".format(
                site_name, address, radius
            )
            % target_scores[site_name][1]
        )

        for node in nodes_sample.index:
            try:
                route = nx.shortest_path(
                    G, source=node, target=target_node, weight="length"
                )  # calculate route from target node to sample node
                list_of_routes.append(route)  # append the length to the list
            except Exception:
                pass
        target_to_node_routes[site_name] = list_of_routes

        site_names.append(site_name)
        i += 1
    return target_to_node_routes, target_scores, site_names


def generate_route_layers(
    networkx_dict,
    target_to_node_routes,
    site_names,
    list_of_target_addresses,
    target_scores,
    colors=["green", "red", "yellow", "blue", "pink", "purple"],
):
    """Function to plot routes from target nodes to sample nodes for on a folium map

    Args:
        G: Networkx graph of area
        target_to_node_routes: Dict of site names to list of routes from that node to target
        site_names: list of sites
        list_of_target_addresses: list of target addresses (same length & order as site names)
        list_of_target_coords: list of target coords (same length & order as site names)
        target_scores: score for each target
        colors: (optional) colors for routes for each site

    Returns:
        Single folium map with all routes and markers with one layer per site
    """
    result = []
    for i, (site, target_address) in enumerate(
        zip(site_names, list_of_target_addresses)
    ):
        G = networkx_dict[target_address]["map"]
        target_coords = ox.geocode(target_address)
        layer = routes_to_featuregroup(
            G, routes=target_to_node_routes[site], color=colors[i], name=site
        )
        iframe = folium.IFrame(
            '<font face = "Arial"><b>{}:</b> {}. <br><br><b>{} Score:</b> {}</br></br></font>'.format(
                site, target_address, site, target_scores[site]
            )
        )
        popup = folium.Popup(iframe, min_width=200, max_width=300)
        folium.Marker(
            location=target_coords,
            popup=popup,
            icon=folium.Icon(color=colors[i], icon="info-sign"),
        ).add_to(layer)
        result.append(layer)
    return result


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
    for route in routes:
        route_coords = []
        for node in route:
            route_coords.append((G.nodes[node]["y"], G.nodes[node]["x"]))
        lines.append(route_coords)
    folium.PolyLine(lines, color=color, weight=2, opacity=0.5).add_to(layer)

    return layer


def generate_lsoa_layer(remapped_lsoa, color="blue"):
    layer = folium.FeatureGroup(name="LSOAs")
    style = {"color": color}

    shape = folium.GeoJson(data=remapped_lsoa, style_function=lambda x: style)
    shape.add_to(layer)
    return layer


# function to plot each of the routes from the target node to the sample nodes as a folium map and add a marker for the target node
# save each of the folium maps as a folium object in the list route_maps to be displayed by streamlit
def generate_route_maps(
    networkx_dict,
    target_to_node_routes,
    site_names,
    list_of_target_addresses,
    target_scores,
):
    route_maps = []
    for site, address in zip(site_names, list_of_target_addresses):
        G = networkx_dict[address]["map"]

        target_coords = ox.geocode(address)
        target_node = ox.get_nearest_node(G, target_coords)

        route_map = ox.plot_route_folium(
            G, target_to_node_routes[site][0], route_color="#ff0000", opacity=0.5
        )
        for route in target_to_node_routes[site][1 : len(target_to_node_routes[site])]:
            route_map = ox.plot_route_folium(
                G, route, route_map=route_map, route_color="#ff0000", opacity=0.5
            )

        iframe = folium.IFrame(
            '<font face = "Arial"><b>{}:</b> {}. <br><br><b>{} Score:</b> {}</br></br></font>'.format(
                site, address, site, target_scores[site]
            )
        )
        popup = folium.Popup(iframe, min_width=200, max_width=300)
        folium.Marker(location=target_coords, popup=popup).add_to(route_map)
        route_maps.append(route_map)
    return route_maps


# save each of the folium maps as a folium object in the list route_maps to be displayed by streamlit
def save_maps(site_names, route_maps):
    for site_name, map in zip(site_names, route_maps):
        map.save("route map for {}.html".format(site_name))


# main function to generate networkx map then generate the scores and folium map for each proposed target location
def mclp_main(list_of_target_addresses, radius):
    lsoa_names = get_lsoas_from_postcode(list_of_target_addresses)
    neighboring_polys_dict, remapped_lsoas_dict = generate_neighboring_polys(
        list_of_target_addresses, lsoa_names, radius
    )
    networkx_dict = generate_networkx(
        list_of_target_addresses, neighboring_polys_dict, type
    )
    dict_of_nodes_samples = generate_nodes_samples(
        list_of_target_addresses, neighboring_polys_dict, networkx_dict
    )
    (
        target_to_node_routes,
        target_scores,
        site_names,
    ) = generate_target_routes_and_scores(
        networkx_dict, dict_of_nodes_samples, list_of_target_addresses, radius
    )

    first_target = ox.geocode(list_of_target_addresses[0])

    map = folium.Map(location=first_target, tiles="cartodbpositron", zoom_start=13)

    generate_lsoa_layer(remapped_lsoas_dict[lsoa_names[0]], color="blue").add_to(map)

    layers = generate_route_layers(
        networkx_dict,
        target_to_node_routes,
        site_names,
        list_of_target_addresses,
        target_scores,
    )
    for layer in layers:
        layer.add_to(map)

    # TO DO: keep in front doesnt work to move lsoa's behind route layers on folium map

    # add a layer control to toggle the layers on and off
    folium.LayerControl().add_to(map)
    # save_maps(site_names, route_map)
    return target_scores, map


# call main function mclp_main(['postcode1', 'postcode2'], radius=500) to generate target_scores and route maps
