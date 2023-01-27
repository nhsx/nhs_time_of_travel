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


def app():
    

    st.title("Specify the search area")

    st.markdown(
        """
        An interactive web app for medical siting called Medmap.
        
    """
    )



def main():
    data_uploader()
    app()

    if 'df' in globals():
        searchcheckbox_town = st.checkbox("City or Town ",value = False,key=12)
        searchcheckbox_county = st.checkbox("County", value= False, key=13)

    if searchcheckbox_town:
        town_search = st.text_input("town")
    else:
        town_search = ''

    if searchcheckbox_county:
        county_search = st.text_input("County")
    else:
        county_search = ''


    if st.button("search"):
        # 1. only City/Town is checked
        if searchcheckbox_town:
            # if town is specified but not the county
            if town_search != '' and county_search == '':
                df_result_search = df[df['City'].str.contains(town_search, case=False, na=False)]
            # if county is specified but not the town
            elif town_search == '' and county_search != '':
                df_result_search = df[df['County'].str.contains(county_search, case=False, na=False)]
            # if both city and County are specified
            elif town_search != '' and county_search != '':
                df_result_search = df[(df['City'].str.contains(town_search, case=False, na=False)) & (df['County'].str.contains(county_search, case=False, na=False))]
            # if user does not enter anything
            else:
                st.warning('Please enter at least a Town or a County')


        # 3. if both Town/City and County are checked
        else:
            pass  # continue here.

        st.write("{} Records ".format(str(df_result_search.shape[0])))
        st.dataframe(df_result_search)


        
        
            

if __name__== "__main__":
    main()


