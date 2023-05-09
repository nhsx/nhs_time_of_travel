import streamlit as st
from functions.uploader import uploader as up


def sidebar(uploader: bool):
    with st.sidebar:
        if uploader == True:
            file = st.file_uploader(
                "Upload your excel from the template, or use one of our datasets, hospital.csv or epraccur.csv (for gp practices)",
                type=["xls", "xlsx"],
            )

            df, fn = up(file)

        st.title("About")
        st.info(
            """
        Developed by: NHS England

        GitHub repository: <https://github.com/nhs-pycom/nhs_time_of_travel>
        """
        )
        if uploader == True:
            return df, fn
