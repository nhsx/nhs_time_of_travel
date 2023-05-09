import streamlit as st
import pandas as pd
import numpy as np
import pathlib
import os
import openpyxl

# hospital = '/Users/oliver.jones/Documents/GitHub/pycom_nhs_time_of_travel/streamlit/streamlit/data/Hospital.csv'
# hospital = '/Users/oliver.jones/Documents/GitHub/pycom_nhs_time_of_travel/streamlit/streamlit/data/Hospital.csv'
hospital = "../data/Hospital.csv"


# @st.cache
def load_data_csv(file):
    return pd.read_csv(file)


# @st.cache
def load_data_xls(file):
    return pd.read_excel(file)


@st.cache
def uploader(file):
    if file is not None:
        df = load_data_xls(file)
        df = df.dropna(subset=["County"])
        # df['Address'] = df[['Address1','Address2','Address3']].astype(str).agg(', '.join,axis=1)
        df["Address"] = df["Address"].str.title()
        df["Address"] = df["Address"].str.replace("Nan", "").str.replace(",", " ")
        # df['Name'] = df['OrganisationName'].str.title()
        df = df[["Name", "Address", "City", "County"]]
        filename = file.name
    else:
        hospital_file = os.path.join(pathlib.Path().resolve(), hospital)
        df = load_data_csv(hospital_file)

        # Remove the repeatitive part of the address fields
        df["Address1"] = df.apply(
            lambda x: "" if str(x["Address1"]) == str(x["Address2"]) else x["Address1"],
            axis=1,
        )
        df["Address2"] = df.apply(
            lambda x: "" if str(x["Address2"]) == str(x["Address3"]) else x["Address2"],
            axis=1,
        )

        # Geocoder understands address with in format of <Part 1 - name of place or building>,<Part 2 - street and number>,<City>,<Postcode>
        # in case we have 3 Addresses fields available, we probably don't need middle part as street and number will be
        # in the Address3 place. For that to make sure that geocoder understands the address, we removing the middle part of it.
        df["Address2"] = df.apply(
            lambda x: ""
            if (
                str(x["Address1"]) not in ["", "nan"]
                and str(x["Address2"]) not in ["", "nan"]
                and str(x["Address3"]) not in ["", "nan"]
            )
            else x["Address2"],
            axis=1,
        )
        df["Address"] = (
            df[["Address1", "Address2", "Address3", "City", "Postcode"]]
            .astype(str)
            .agg(
                lambda x: ",".join(
                    word for word in x if word.strip() != "" and word.strip() != "nan"
                ),
                axis=1,
            )
        )

        df["Name"] = df["OrganisationName"].str.title()
        # We return also Latitude and Longitude as it's already available. From the msr algorithm, it will be used
        # if it's available, but if not, it will obtain it via address search.
        df = df[
            ["Name", "Address", "City", "County", "Latitude", "Longitude", "Postcode"]
        ]
        filename = "Hospital"

    return df, filename
