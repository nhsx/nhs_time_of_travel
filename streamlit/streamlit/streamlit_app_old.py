import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geojson
from scripts.py_walking_gp_practice_cambridge import dis_map

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# 🚂 Travel time to NHS organisations")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    NHS Streamlit geomapping page
"""
)
st.sidebar.title("About")
st.sidebar.info(
"""
Developed by: NHS England

GitHub repository: <https://github.com/nhs-pycom/nhs_time_of_travel>
"""
)

def display_map():

# Download a geoJSON shapefile for the CB postcode areas (Cambirdge, UK) from GitHub
#-----------------------------------------------------------------------------------
    try:
        cb_geo_json_link =  'https://raw.githubusercontent.com/missinglink/uk-postcode-polygons/master/geojson/CB.geojson'
        cam_postcode_shapefile_r = urllib.request.urlopen(cb_geo_json_link)
        cam_postcode_shapefile = geojson.loads(cam_postcode_shapefile_r.read())
    except:
        with open('data/cambridge.geosjon') as f:
            cam_postcode_shapefile = geojson.load(f)


    central_list = []
    postcodes = ["CB1", "CB2", "CB3", "CB4", "CB5"] #---------- the five postcodes defined as being 'central Cambridge'
    postcodes = st.multiselect('Select central postcodes', postcodes)
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

#Adding a toolip which appears on hover to the postcode choropleth layer
#----------------------------------------------------------------------
    data_on_hover = folium.features.GeoJson(data = cam_postcode_shapefile, style_function=style_function, control=False, highlight_function=highlight_function, tooltip=folium.features.GeoJsonTooltip(
        fields= ['name'], 
        aliases=['Postcode: '],
        localize = True))

    map = folium.Map(location=[52.1978,0.1257], zoom_start=9, tiles='CartoDB positron')

    chloro.geojson.add_to(map)


    map.add_child(data_on_hover)
    #map.keep_in_front(data_on_hover)


    st_map = st_folium(map, width=700, height=450)
    #return central_list

# @st.cache
def ren_map():
    # st_map = st_folium(dis_map()[0], width=700, height=450)
    # st_map2 = st_folium(dis_map()[1], width=700, height=450)
    # return st_map, st_map2
    a = dis_map()[0]
    b = dis_map()[1]
    return a, b

# @st.cache
def main(acentral_list='a'):

    # st_map = st_folium(dis_map()[0], width=700, height=450)
    # st_map2 = st_folium(dis_map()[1], width=700, height=450)
    st_map = st_folium(ren_map()[0], width=700, height=450)
    st_map2 = st_folium(ren_map()[1], width=700, height=450)

    # print(ren_map())
    #display_map()

# ren_map()

if __name__ == '__main__':
        main()

