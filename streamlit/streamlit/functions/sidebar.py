import streamlit as st
from functions.uploader import uploader as up

def sidebar(uploader:bool):

    with st.sidebar:
        
        if uploader == True:

            df, fn = up()

        st.title("About")
        st.info(
        """
        Developed by: NHS England

        GitHub repository: <https://github.com/nhs-pycom/nhs_time_of_travel>
        """
        )
        if uploader == True:
            return df, fn
