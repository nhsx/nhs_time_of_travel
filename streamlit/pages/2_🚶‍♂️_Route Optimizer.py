import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import pandas as pd
import geojson
from scripts.py_walking_gp_practice_cambridge import dis_map
import base64
#from uploader import data_uploader
from functions.sidebar import sidebar as sidebar
from scripts.tsp import main as tsp
import osmnx as ox
import networkx as nx
import folium
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import itertools



# NHS Logo
svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 16">
            <path d="M0 0h40v16H0z" fill="#005EB8"></path>
            <path d="M3.9 1.5h4.4l2.6 9h.1l1.8-9h3.3l-2.8 13H9l-2.7-9h-.1l-1.8 9H1.1M17.3 1.5h3.6l-1 4.9h4L25 1.5h3.5l-2.7 13h-3.5l1.1-5.6h-4.1l-1.2 5.6h-3.4M37.7 4.4c-.7-.3-1.6-.6-2.9-.6-1.4 0-2.5.2-2.5 1.3 0 1.8 5.1 1.2 5.1 5.1 0 3.6-3.3 4.5-6.4 4.5-1.3 0-2.9-.3-4-.7l.8-2.7c.7.4 2.1.7 3.2.7s2.8-.2 2.8-1.5c0-2.1-5.1-1.3-5.1-5 0-3.4 2.9-4.4 5.8-4.4 1.6 0 3.1.2 4 .6" fill="white"></path>
          </svg>
"""

# render svg image
def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

render_svg(svg)

st.title("🚶‍♂️ Route Optimizer (aka The Travelling Salesman Problem)")


df2, fn = sidebar(True)

df = df2.copy()

title = f'Loaded: {fn} data- Expand to preview data:'

# st.write('Loaded:', fn, "- Preview of the data:")
with st.expander(title, expanded=False):
    st.write(df.head())
filter = st.checkbox('filter data to City or County', value=True)

if filter:
    options = []
    if 'City' in df.columns:
        options.extend(df['City'].unique())
    if 'County' in df.columns:
        options.extend(df['County'].unique())

    if len(options)>0:

        city_or_county = st.selectbox("Enter Town/City or County (or both)",options=options)    
        filtered_df = df[(df['City'] == city_or_county) | (df['County'] == city_or_county)]
    else:
        filtered_df=df
else:
    filtered_df = df
st.write(filtered_df)


#county= filtered_df['County'].iloc[0]

with st.form('MSR_inputs'):
    start_address_options = list(filtered_df['Address'].unique())

    new_start_address = st.text_input("Enter a new start address (if not in the list above):")
    if new_start_address:
        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.geocode(new_start_address, addressdetails=True)
        new_coord = (location.latitude, location.longitude)
        
        new_entry = {'City': location.raw['address']['city'], 'County': location.raw['address']['county'], 'Address': new_start_address, 'Latitude': new_coord[0], 'Longitude': new_coord[1]}
        filtered_df = filtered_df.append(new_entry, ignore_index=True)
        start_address_options.append(new_start_address)

        # Set the default value of the dropdown to the user-entered address
        start_address = st.selectbox("Select start address from the dataframe above", options=start_address_options, index=len(start_address_options) - 1)
    else:
        start_address = st.selectbox("Select start address from the dataframe above", options=start_address_options)


    network_type = st.selectbox("select network type", ["drive","walk","bike"])
    radius_miles = st.number_input("Enter radius in miles", min_value=1, max_value=5,value=1)
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner('Generating Best Route...........'):

        map, dataframe = tsp(filtered_df, start_address, network_type, radius_miles)
        msr_map = folium_static(map, width=700, height=450)
        st.write(dataframe)