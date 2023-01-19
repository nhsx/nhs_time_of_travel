
import streamlit as st
import pandas as pd

def data_uploader():
  st.set_page_config(page_title="Data Uploader", page_icon=":chart_with_upwards_trend:", layout="wide")
  st.title("Upload Your Data")


# Create a file uploader widget
  file_upload = st.file_uploader("Choose a CSV file", type=["csv"])
  if file_upload is not None:

# Read the CSV file into a pandas DataFrame
    data = pd.read_csv(file_upload)


# Show the first few rows of the data
  st.write("Preview of the data:")
  st.write(data.head())


# Store the data in a global variable
  global df
  df = data


# Let the user know the data has been uploaded successfully
  st.success("Data uploaded successfully!")


