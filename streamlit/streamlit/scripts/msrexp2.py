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

#col1, col2 = st.columns([1,3])
st.title("Multiple Shortest Routes finder")


@st.cache
def load_data(file):
    return pd.read_csv(file)



#def file_process():
def main():

    
    file = st.file_uploader("Upload your CSV from the template, or use one of our datasets, hospital.csv or epraccur.csv (for gp practices)", type= ["csv"])
    if file is not None:
        df = load_data(file)
        df = df.dropna(subset=['County'])
        df['Address'] = df[['Address1','Address2','Address3']].astype(str).agg(', '.join,axis=1)
        df['Address'] = df['Address'].str.title() 
        df['Address'] = df['Address'].str.replace('Nan', '').str.replace(',', ' ')
        df['Name'] = df['OrganisationName'].str.title()
        df = df[['Name', 'Address','City','County']]

    #with col2:
            # Show the first few rows of the data
        st.write("Preview of the data:")
        st.write(df.head())

        city_or_county = st.selectbox("Enter Town/City or County (or both)",options=df['City'])
        filtered_df = df[(df['City'] == city_or_county) | (df['County'] == city_or_county)]
        st.write(filtered_df)
        target_address = st.text_input("Enter target address in following format; 2 Hill Road, Cambridge")
        network_type = st.selectbox("select network type", ["all","drive","walk","bike"])
        
        #G = ox.graph_from_place(city_or_county, network_type=network_type)

        if st.button("Filter dataframe and run map of target Town/City/County"):
            if filtered_df.empty:
                st.write("no data found for entered city or county")
            else:
                
             
             
                #fig,ax = ox.plot_graph(ox.project_graph(G),show=False,close=False, node_size=0, bgcolor='k')
                #st.pyplot(fig)
                #st.write("source address/ addresses")
                #st.write(filtered_df)


                #if st.button("Find shortest routes"):
                ox.config(log_console=True, use_cache=True)
                target_location = ox.geocode(target_address)
                G = ox.graph_from_place(city_or_county, network_type=network_type)
                target = ox.nearest_nodes(G, target_location[1],Y=target_location[0])

                coords = []
                for address in filtered_df['Address']:
                    try:
                        coords.append(ox.geocoder.geocode(address))
                    except Exception as e:
                        pass
                list=[]
                for i,c in enumerate(coords):
                    list.append(ox.nearest_nodes(G,X=coords[i][1],Y=coords[i][0]))
                routes = []
                for i,a in enumerate(list):
                    routes.append(nx.shortest_path(G,list[i],target,weight="length"))
                lengths=[]
                for i,b in enumerate(routes):
                    lengths.append(nx.shortest_path_length(G,source=list[i],target=target,weight='length'))
                filtered_df['lengths'] = np.array(lengths)
                #Gx = ox.plot_graph_routes(G, routes, route_color='r', route_linewidth=6, bgcolor='k')
                #route_map = ox.plot_route_folium(G, routes[0], route_color = '#ff0000', opacity = 0.5)
                route_map = ox.plot_route_folium(G,routes[0])
                for route in routes:
                        route_map = ox.plot_route_folium(G, route, route_map = route_map)
                iframe = folium.IFrame('<font face = "Arial"><b>{}</b> {}.</font>'.format(target_address,target_location))
                popup = folium.Popup(iframe, min_width=200, max_width=200)
                folium.Marker(location=target_location,popup = popup).add_to(route_map)
                
                
                route_map


                

                st.write(filtered_df)




if __name__ == '__main__':
    main()