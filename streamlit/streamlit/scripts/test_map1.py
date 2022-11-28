# Import Python libraries (use Python >= v. 3.9.0)
#-------------------------------------------------

import networkx as nx
import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import urllib.request
import pandas as pd
import zipfile
import folium
import geojson

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from descartes import PolygonPatch
from shapely.geometry import Point
from shapely.ops import cascaded_union


# Download a geoJSON shapefile for the CB postcode areas (Cambirdge, UK) from GitHub
#-----------------------------------------------------------------------------------
try:
    cb_geo_json_link =  'https://raw.githubusercontent.com/missinglink/uk-postcode-polygons/master/geojson/CB.geojson'
    cam_postcode_shapefile_r = urllib.request.urlopen(cb_geo_json_link)
    cam_postcode_shapefile = geojson.loads(cam_postcode_shapefile_r.read())
except:
    with open('data/cambridge.geosjon') as f:
        cam_postcode_shapefile = geojson.load(f)


# Create the a pandas dataframe which define 5 'central Cambridge' postcodes (to allow for these areas to be visualised in a differnt colour in the choropleth layer)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

central_list = []
postcodes = ["CB1", "CB2", "CB3", "CB4", "CB5"] #---------- the five postcodes defined as being 'central Cambridge'
geometry_list = cam_postcode_shapefile['features']
for geometry in geometry_list:
    if geometry['properties']['name'] in postcodes:
        data_cam = [geometry['properties']['name'],1] #---------- Central Postcodes asigned a value of 1 
        central_list.append(data_cam)
    else:
        data_cam = [geometry['properties']['name'],0] #---------- Other Postcodes asigned a value of 0
        central_list.append(data_cam)
post_code_df = pd.DataFrame(central_list, columns = ['Postcode', 'Central Cambridge']) 
post_code_df['Postcode'] = post_code_df['Postcode'].astype(str)

#Create a folium map visualising the areas covered by the Cambridge Postcodes
#----------------------------------------------------------------------------

#Defines the highlight and popup style for the choropleth layer
#--------------------------------------------------------------
style_function = lambda x: {'fillColor': '#ffffff', 
                            'color':'#000000', 
                           'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 
                                'color':'#000000', 
                                'fillOpacity': 0.5, 
                                 'weight': 0.1}

#Create the frame and background folium map 
#------------------------------------------
frame = folium.Figure(width=500, height=500) #------ Map centred on Cambridge using coordinates
cambridge_map = folium.Map(
    location=[52.21, 0.15], 
    tiles="cartodbpositron",
    zoom_start=9).add_to(frame)

#Add a choropleth with the Cambridge postcode areas (with central postcodes differently coloured using the post_code_df)
#------------------------------------------------------------------------------------------------------------------------
chloro = folium.Choropleth(
    geo_data= cam_postcode_shapefile,
    data=post_code_df,
    name = 'Cambridge Postcodes',
    columns= ['Postcode', 'Central Cambridge'],
    key_on='feature.properties.name',
    fill_color="RdBu",
    fill_opacity=0.7,
    line_opacity=1,
    highlight = True,
   )

#Adding a toolip which appears on hover to the postcode choropleth layer
#----------------------------------------------------------------------
data_on_hover = folium.features.GeoJson(data = cam_postcode_shapefile, style_function=style_function, control=False, highlight_function=highlight_function, tooltip=folium.features.GeoJsonTooltip(
    fields= ['name'], 
    aliases=['Postcode: '],
    localize = True))

#Removes the automatically generated folium legend from the map
#--------------------------------------------------------------
for key in chloro._children:
    if key.startswith('color_map'):
        del(chloro._children[key])
#--------------------------------------------------------------

cambridge_map.add_child(data_on_hover)
cambridge_map.keep_in_front(data_on_hover)
chloro.add_to(cambridge_map)
folium.LayerControl().add_to(cambridge_map)

#Saves the folium map as an html object for use in the webpage
#--------------------------------------------------------------
cambridge_map.save('images/folium/cambridge_postcode_map.html', "w")