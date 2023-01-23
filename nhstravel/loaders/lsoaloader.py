import pandas as pd
import urllib.request
import geojson
import copy
from pandas.io.parsers.readers import TextFileReader
from pandas import DataFrame

# LSOA data set locations
lsoa_definitions_data_path  = 'data/lower_layer_super_output_areas_december_2021.csv'
lsoa_popupation_data_path   = 'data/lsoa_global_number_residents_2021.csv'

# LSOA data column names
lsoa_object_id_col  = 'OBJECTID'
lsoa_code_col       = 'LSOA21CD'
lsoa_name_col       = 'LSOA21NM'
lsoa_population_col = 'all ages'

def read_lsoa_objects_england(lsoa_data_path:str = lsoa_definitions_data_path, 
                              object_id_col_number:int = 0,
                              lsoa_code_col_number:int = 1,
                              lsoa_name_col_number:int = 2,
                              lsoa_global_id_col_number:int = 3) -> TextFileReader:
    """
    Reads the CSV file with lsoa data definitions
    Parameters 
    lsoa_data_path: 
        Path to the lsoa data file.
    object_id_col_number:
        Column number in the CSV file containing object id for LSOA.
    lsoa_code_col_number:
        Column number in the CSV file containing LSOA code.
    lsoa_name_col_number:
        Column number in the CSV file containing LSOA name.
    lsoa_global_id_col_number:
        Columne number in the CSV file containing LSOA global id.
    return:
        Text file reader object which can be passed to pandas to create data frame
        or can be manipulated directly.
    """
    global_lsoa_pd  = pd.read_csv(
        lsoa_data_path, 
        header=0, 
        usecols=[
            object_id_col_number, 
            lsoa_code_col_number,
            lsoa_name_col_number,
            lsoa_global_id_col_number], 
        dtype='string')
    
    return global_lsoa_pd

def read_lsoa_population_estimates_england(lsoa_data_path:str = lsoa_popupation_data_path,
                                           skip_rows:int = 9,
                                           lsoa_code_col_number:int = 1,
                                           lsoa_name_col_number:int = 0,
                                           lsoa_population_col_number:int = 2) -> TextFileReader:
    """
    Read the CSV file with population figures from each LSOA
    Parameters
    lsoa_data_path:
        Path to the CSV file
    skip_rows:
        How many rows at the start of the file to skip. Many files contain description
        information at the start of the file, which will disrupt loading the data.
        Specifying number of rows to skip will allow reader to concentrate on the data rows
    lsoa_code_col_number:
        Column number in the CSV containing LSOA code
    lsoa_name_col_number:
        Column number in the CSV containing LSOA name
    lsoa_population_col_number:
        Column number in the CSV containing the population estimates
    return:
        Text file reader object with can be passed to pandas to create data frame
        or can be manipulated directly
    """
    global_lsoa_population_estimates_2021_pd = pd.read_csv(
        lsoa_data_path,
        header=0, 
        skiprows=skip_rows,
        usecols=[
            lsoa_code_col_number,
            lsoa_name_col_number,
            lsoa_population_col_number
        ], 
        names=[
            lsoa_name_col,
            lsoa_code_col,
            lsoa_population_col 
            ], 
    dtype='string')
    
    return global_lsoa_population_estimates_2021_pd

def load_lsoa_objects_for_area_england(area:str,
                                       global_lsoa:TextFileReader = None) -> DataFrame:
    """
    Loads lsoa object for england and returning data frame containing only LSOAs
    for the passed area
    Parameters
    area:
        The name or partial name for the area to be returned. The matching of the area
        is done by matching the LSOA name. For example, passing area=Cambridge, will 
        return LSOAs for Cambridge and Cambridgeshire
    returns:
        Pandas dataframe with loaded LSOAs
    """
    if global_lsoa is None:
        global_lsoa = read_lsoa_objects_england()
    
    area_lsoa_pd = DataFrame(
        global_lsoa[global_lsoa[lsoa_name_col].str.contains(area)])
    area_lsoa_pd.reset_index(drop=True, inplace=True)
    area_lsoa_pd[lsoa_object_id_col] = area_lsoa_pd[lsoa_object_id_col].astype(int)
    area_lsoa_pd[lsoa_code_col] = area_lsoa_pd[lsoa_code_col].astype(str)
    
    return area_lsoa_pd

def load_lsoa_population_estimates_england(area:str, 
                                           global_lsoa_population_estimates:TextFileReader = None) -> DataFrame:
    """
    Loads the LSOA population estimates for area in England
    Parameters:
    area:
        The name or partial name for the area to be returned. The matching of the area
        is done by matching the LSOA name. For example, passing area=Cambridge, will 
        return LSOAs for Cambridge and Cambridgeshire
    global_lsoa_population_estimates:
        Text file reader where the population can be loaded from. In case the file reader is None
        the LSOA will be loaded from default lsoa_popupation_data_path
    return:
        Pandas dataframe with loaded LSOAs and population
    """
    if global_lsoa_population_estimates is None:
        global_lsoa_population_estimates = read_lsoa_population_estimates_england()
    
    lsoa_population_estimates_pd = DataFrame(
        global_lsoa_population_estimates[global_lsoa_population_estimates[lsoa_name_col].str.contains(area)])
    lsoa_population_estimates_pd.reset_index(drop=True, inplace=True)
    lsoa_population_estimates_pd[lsoa_population_col] = lsoa_population_estimates_pd[lsoa_population_col].str.replace(',', '').astype(int)
    
    return lsoa_population_estimates_pd


def build_lsoa_data_frame_for_area_england(area:str) -> DataFrame:
    """
    Loads and builds data frame containing information about LSOA and population 
    for provided area in England
    Parameters:
    area:
        The name or partial name for the area to be returned. The matching of the area
        is done by matching the LSOA name. For example, passing area=Cambridge, will 
        return LSOAs for Cambridge and Cambridgeshire
    return:
         Pandas dataframe with loaded LSOAs and population
    """
    lsoa_df = load_lsoa_objects_for_area_england(area)
    lsoa_population_df = load_lsoa_population_estimates_england(area)
    # Dropping the duplicate column before the merge
    lsoa_population_df.drop(columns=[lsoa_name_col], inplace=True)

    lsoa_with_population_pd = pd.merge(
        lsoa_df, 
        lsoa_population_df, 
        left_on=lsoa_code_col, 
        right_on=lsoa_code_col)
    lsoa_with_population_pd[lsoa_object_id_col] = lsoa_with_population_pd[lsoa_object_id_col].astype(str)
    
    return lsoa_with_population_pd

def load_geo_json_shapefiles_for_lsoas(lsoas:DataFrame, 
                                       area:str = None) -> dict:
    """
    Loads geojson shape files for provided lsoas
    Parameters
    lsoas:
        Pandas dataframe containing object ids for all lsoas to load
    area:
        Area to filter lsoas by. The loading method split object ids
        to chunks to allow faster loading and prevent throttling from 
        the geoportal. This means that it can load lsoas for areas
        outside of the area of interest. Providing area will ensure
        lsoas will be filtered by the area and only those will be returned.
    return:
        dictionary of all lsoas geojson keyed by the lsoa code
    """
    # Create split of objects to chunks
    object_ids_chunks = [[]]
    prev_objid = lsoas[lsoa_object_id_col].min()
    for _, row in lsoas.iterrows():
        current_objid = row[lsoa_object_id_col]
        if int(current_objid) - int(prev_objid) > 1:
            object_ids_chunks.append([])
        object_ids_chunks[-1].append(current_objid)
        prev_objid = current_objid

    # Load the LSOA geofiles from the arcgis and merge into one geogson file for processing
    # obtained via https://geoportal.statistics.gov.uk/datasets/ons::lsoa-dec-2021-boundaries-full-clipped-ew-bfc/about
    lsoa_shapefile = None
    for chunk in object_ids_chunks:
        geo_json_url_link =  f"https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LSOA_Dec_2021_Boundaries_Full_Clipped_EW_BFC_2022/FeatureServer/0/query?where=OBJECTID>={chunk[0]}%20AND%20OBJECTID<={chunk[-1]}&outFields=*&outSR=4326&f=geojson"
        lsoa_shapefile_r = urllib.request.urlopen(geo_json_url_link)
        lsoa_shapefile_all = geojson.loads(lsoa_shapefile_r.read())
        if lsoa_shapefile is not None:
            lsoa_shapefile['features'] = lsoa_shapefile_all['features'] + lsoa_shapefile['features']
        else:
            lsoa_shapefile = lsoa_shapefile_all


    # Return all loaded LSOAs if no further filtering is requested
    remapped_lsoa = copy.deepcopy(lsoa_shapefile)
    if area is None or area.strip() == "":
        return remapped_lsoa
    
    # Filter LSOAs from area only
    # Loading by OBJECTID could bring additional objects not in the area
    remapped_lsoa['features'] = []
    for feature in lsoa_shapefile['features']:
        row_json = lsoas.loc[lsoas[lsoa_code_col] == feature['properties'][lsoa_code_col]].to_dict(orient="records")
        if len(row_json):
            feature['properties'] =  {**feature['properties'], **row_json[0]}
            remapped_lsoa['features'].append(copy.deepcopy(feature))

    return remapped_lsoa
