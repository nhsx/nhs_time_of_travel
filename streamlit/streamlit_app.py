!conda install cartopy
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geojson
import base64
from scripts.py_walking_gp_practice_cambridge import dis_map
from functions.sidebar import sidebar as sidebar

st.set_page_config(
    page_title="NHS Time to travel",
  page_icon="https://www.england.nhs.uk/wp-content/themes/nhsengland/static/img/favicon.ico")

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

st.title("🚂 MedMap - NHS Geospatial Tool")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    Medical Map - NHS Streamlit geomapping tool

    This work was led by Paul Carroll, Senior Data Scientist, Oliver Jones, Muhammed-Faaiz Shawanas, Mary Amanuel, as part of their roles with the Digital Analytics and Research Team at NHS England, and Nick Fortescue and Max Morozov, two brilliant engineers at GoogleHealth.

    The following page and accompanying GitHub repository contain the initial proof of concept and exploratory analysis for the design of a holistic and interactive mapping tool to support decision-making in health and social care.

    A mapping tool could support national and regional commissioning strategies by facilitating the placement of new services and the reconfiguration of existing ones. It could also contribute to the NHS agenda for tackling health inequalities by enabling evidence-based decision-making by providing insight on how the availability of health and social care services is influenced by sociodemographic factors.

    Using open-source software and publicly accessible datasets we're able to show three pages so far here; The first Multiple Shortest Routes, and can be used for staff routes to work; The second, Max Coverage Location, this can be used to score a site, e.g. a covid site or a new GP practice; Third the Travelling Salesman Problem, In health context this can be used for district nurse visits, or ambulance drop-offs. 

    Please reach out if you have page suggestions, or wish to contribute. Either raise an issue on the Github site, or email paul.carroll9@nhs.net, or github.com/pauliecarroll.  Thank you.

    Source page: https://nhsx.github.io/nhs_time_of_travel/
    
    Project board: https://github.com/orgs/nhs-pycom/projects/9/views/1
"""
)

sidebar(False)
