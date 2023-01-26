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
    
    today = date.today()

    st.title("Upload or format Hospital.csv")

    st.markdown(
        """
        An interactive web app for called Medmap.
        
    """
    )

    row1_col1, row1_col2 = st.columns([2, 1])

    if st.session_state.get("zoom_level") is None:
        st.session_state["zoom_level"] = 4

    st.session_state["ee_asset_id"] = None
    st.session_state["bands"] = None
    st.session_state["palette"] = None
    st.session_state["vis_params"] = None

    with row1_col1:
        st.write("Preview of the data:")
        st.write(data.head())

    with row1_col2:

        keyword = st.text_input("Search for a location:", "")
        if keyword:
            hospital = hospitals[(hospitals['City'].str.contains (keyword))].reset_index(drop = True)
            hospital['Address'] = hospital[['Address2', 'Address3', 'City','County',]].astype(str).agg(', '.join, axis=1)
            hospital['Address'] = hospital['Address'].str.title() 
            hospital['Address'] = hospital['Address'].str.replace('Nan', '').str.replace(' ,', ' ')
            hospital['Name'] = hospital['OrganisationName'].str.title()
            hospital = hospital[['Name', 'Address']]
    '''
            return hospital
            locations = geemap.geocode(keyword)
            if locations is not None and len(locations) > 0:
                str_locations = [str(g)[1:-1] for g in locations]
                location = st.selectbox("Select a location:", str_locations)
                loc_index = str_locations.index(location)
                selected_loc = locations[loc_index]
                lat, lng = selected_loc.lat, selected_loc.lng
                folium.Marker(location=[lat, lng], popup=location).add_to(m)
                m.set_center(lng, lat, 12)
                st.session_state["zoom_level"] = 12
'''

def main():
    data_uploader()

    if 'df' in globals():
        searchcheckbox_town_county = st.checkbox("City/Town or County ",value = False,key=1)

    if searchcheckbox_town_region:
        town_search = st.text_input("town")
        county_search = st.text_input("county")
    else:
        town_search = ''
        county_search = ''


    if st.button("search"):
        # 1. only name/nickname is checked
        if searchcheckbox_town_county:
            # if town is specified but not the region/ county
            if town_search != '' and county_search == '':
                df_result_search = df[df['Town'].str.contains(town_search, case=False, na=False)]
            # if county is specified but not the town
            elif town_search == '' and county_search != '':
                df_result_search = df[df['County'].str.contains(county_search, case=False, na=False)]
            # if both name and nickname are specified
            elif town_search != '' and county_search != '':
                df_result_search = df[(df['town'].str.contains(town_search, case=False, na=False)) & (df['nickname'].str.contains(nickname_search, case=False, na=False))]
            # if user does not enter anything
            else:
                st.warning('Please enter at least a Town or a County')

        # 3. if both name/nickname and age are checked
        else:
            pass  # continue here.

        st.write("{} Records ".format(str(df_result_search.shape[0])))
        st.dataframe(df_result_search)
            # Do something with the data, for example,
            # create a geospatial plot using the longitude and latitude columns

        
        
            

if __name__== "__main__":
    main()


