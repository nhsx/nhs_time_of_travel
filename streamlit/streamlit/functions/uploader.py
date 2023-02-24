import streamlit as st
import pandas as pd

hosptial = '/Users/oliver.jones/Documents/GitHub/pycom_nhs_time_of_travel/streamlit/streamlit/data/Hospital_orig.csv'

@st.cache
def load_data_csv(file):
    return pd.read_csv(file)

@st.cache
def load_data_xls(file):
    return pd.read_excel(file)

def uploader():
    file = st.file_uploader("Upload your excel from the template, or use one of our datasets, hospital.csv or epraccur.csv (for gp practices)", type= ["xls","xlsx"])
    if file is not None:
        df = load_data_xls(file)
        df = df.dropna(subset=['County'])
        # df['Address'] = df[['Address1','Address2','Address3']].astype(str).agg(', '.join,axis=1)
        df['Address'] = df['Address'].str.title() 
        df['Address'] = df['Address'].str.replace('Nan', '').str.replace(',', ' ')
        # df['Name'] = df['OrganisationName'].str.title()
        df = df[['Name', 'Address','City','County']]
        filename = file.name
    else:
        df = load_data_csv(hosptial)
        df = df.dropna(subset=['County'])
        df['Address'] = df[['Address1','Address2','Address3']].astype(str).agg(', '.join,axis=1)
        df['Address'] = df['Address'].str.title() 
        df['Address'] = df['Address'].str.replace('Nan', '').str.replace(',', ' ')
        df['Name'] = df['OrganisationName'].str.title()
        df = df[['Name', 'Address','City','County']]
        filename = 'Hosptial'
    
    return df, filename
