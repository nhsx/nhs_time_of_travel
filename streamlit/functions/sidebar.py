import streamlit as st
from functions.uploader import uploader as up


def sidebar(uploader: bool):
    with st.sidebar:
        if uploader == True:
            file_type = st.selectbox(
                "Select file to load or upload your own", ["Hospital", "Epraccur"]
            )
            file = st.file_uploader(
                "Upload your excel from the template, or use one of our datasets, hospital.csv or epraccur.csv (for gp practices)",
                type=["xls", "xlsx"],
            )
            print(f"file type = {file_type}")
            df, fn = up(file, file_type)

        st.title("About")
        st.info(
            """
        Developed by: NHS England

        GitHub repository: <https://github.com/nhs-pycom/nhs_time_of_travel>
        """
        )
        if uploader == True:
            return df, fn
