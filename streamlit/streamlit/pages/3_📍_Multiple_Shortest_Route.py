import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
import pandas as pd
import geojson
import base64
from functions.uploader import uploader as up
from scripts.msr import main as msr

st.set_page_config(
    page_title="NHS - Multiple Shortest Route",
    page_icon="📍",
)

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

st.title("📍 Multiple Shortest Route")

st.sidebar.title("About")
st.sidebar.info(
"""
Developed by: NHS England

GitHub repository: <https://github.com/nhs-pycom/nhs_time_of_travel>
"""
)

with st.sidebar:
    df, fn = up()


st.write('Loaded:', fn, "- Preview of the data:")
st.write(df.head())

city_or_county = st.selectbox("Enter Town/City or County (or both)",options=df['City'].unique())
filtered_df = df[(df['City'] == city_or_county) | (df['County'] == city_or_county)]
st.write(filtered_df)

with st.form('MSR_inputs'):

    target_address = st.text_input("Enter target address in following format; 2 Hill Road, Cambridge")
    network_type = st.selectbox("select network type", ["all","drive","walk","bike"])

    submitted = st.form_submit_button("Submit")
    

if submitted:
    st.write('Generating shortest route')
    map, dataframe = msr(city_or_county, filtered_df, target_address, network_type)
    msr_map = folium_static(map, width=700, height=450)
    st.write(dataframe)