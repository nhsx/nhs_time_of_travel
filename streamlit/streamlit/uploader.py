import streamlit as st
import pandas as pd

def data_uploader():
<<<<<<< HEAD
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
=======
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

def main():
    data_uploader()
    if 'df' in globals():
        # Do something with the data, for example,
        # create a geospatial plot using the longitude and latitude columns
        st.deck_gl_chart(
            viewport={
                "latitude": df["latitude"].mean(),
                "longitude": df["longitude"].mean(),
                "zoom": 11,
                "pitch": 50,
            },
            layers=[
                {
                    "type": "ScatterplotLayer",
                    "data": df,
                    "getRadius": 1000,
                    "getFillColor": [255, 0, 0],
                    "pickable": True,
                }
            ],
        )
if __name__== "__main__":
    main()
>>>>>>> e6958b0 (uploader.py)


