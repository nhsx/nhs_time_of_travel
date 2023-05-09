import pandas as pd
import urllib.request
import geojson
import copy
from pandas.io.parsers.readers import TextFileReader
from pandas import DataFrame
import os

# LSOA data set locations
data_path = os.path.dirname(__file__) + "/../../data"
lsoa_definitions_data_path = (
    data_path + "/lower_layer_super_output_areas_december_2021.csv"
)
lsoa_population_data_path = data_path + "/lsoa_global_number_residents_2021.csv"
lsoa_postcode_map_data_path = data_path + "/pcd_lsoa21cd_nov22_en.csv"


class LsoaLoader:
    def __init__(
        self,
        definitions_data_path: str = None,
        population_data_path: str = None,
        defs_object_id_col_number: int = 0,
        defs_code_col_number: int = 1,
        defs_name_col_number: int = 2,
        defs_global_id_col_number: int = 3,
        population_skip_rows: int = 9,
        population_code_col_number: int = 1,
        population_name_col_number: int = 0,
        population_population_col_number: int = 2,
    ):
        """
        Create a loader which will load data about LSOAs from commonly provided CSV formats.
        Args:
            definitions_data_path: Path to the lsoa data file.
            population_data_path: Path to a CSV file containing LSOA population estimates
            defs_object_id_col_number: Column number in the definitions CSV file containing object id for LSOA.
            defs_code_col_number: Column number in the definitions CSV file containing LSOA code.
            defs_name_col_number: Column number in the definitions CSV file containing LSOA name.
            defs_global_id_col_number: Column number in the definitions CSV file containing LSOA global id.
            population_skip_rows: How many rows at the start of the file to skip. Many files contain description
                information at the start of the file, which will disrupt loading the data.
                Specifying number of rows to skip will allow reader to concentrate on the data rows
            population_code_col_number: Column number in the CSV containing LSOA code
            population_name_col_number: Column number in the CSV containing LSOA name
            population_population_col_number: Column number in the CSV containing the population estimates
        """
        data_path = os.path.dirname(__file__) + "/../../data"
        if definitions_data_path is not None:
            self.definitions_data_path = definitions_data_path
        else:
            self.definitions_data_path = (
                data_path + "/lower_layer_super_output_areas_december_2021.csv"
            )
        if population_data_path is not None:
            self.population_data_path = population_data_path
        else:
            self.population_data_path = (
                data_path + "/lsoa_global_number_residents_2021.csv"
            )
        # LSO data column indices from the definition file
        self.defs_object_id_col_number = defs_object_id_col_number
        self.defs_code_col_number = defs_code_col_number
        self.defs_name_col_number = defs_name_col_number
        self.defs_global_id_col_number = defs_global_id_col_number
        # default rows to skip in the definitions file
        self.population_skip_rows = population_skip_rows
        self.population_code_col_number = population_code_col_number
        self.population_name_col_number = population_name_col_number
        self.population_population_col_number = population_population_col_number
        # LSOA data column names in population file
        self.lsoa_object_id_col = "OBJECTID"
        self.lsoa_code_col = "LSOA21CD"
        self.lsoa_name_col = "LSOA21NM"
        self.lsoa_population_col = "all ages"

    def read_lsoa_objects_england(self) -> TextFileReader:
        """
        Reads the CSV file with lsoa data definitions.

        Returns:
            Text file reader object which can be passed to pandas to create data frame
            or can be manipulated directly.
        """
        global_lsoa_pd = pd.read_csv(
            self.definitions_data_path,
            header=0,
            usecols=[
                self.defs_object_id_col_number,
                self.defs_code_col_number,
                self.defs_name_col_number,
                self.defs_global_id_col_number,
            ],
            dtype="string",
        )
        return global_lsoa_pd

    def read_lsoa_population_estimates_england(self) -> TextFileReader:
        """
        Read the CSV file with population figures from each LSOA.

        Returns:
            Text file reader object with can be passed to pandas to create data frame
            or can be manipulated directly
        """
        global_lsoa_population_estimates_2021_pd = pd.read_csv(
            self.population_data_path,
            header=0,
            skiprows=self.population_skip_rows,
            usecols=[
                self.population_code_col_number,
                self.population_name_col_number,
                self.population_population_col_number,
            ],
            names=[self.lsoa_name_col, self.lsoa_code_col, self.lsoa_population_col],
            dtype="string",
        )

        return global_lsoa_population_estimates_2021_pd

    def load_lsoa_objects_for_area_england(
        self, area: str, global_lsoa: TextFileReader = None
    ) -> DataFrame:
        """
        Loads LSOA object for england and returning data frame containing only LSOAs
        for the passed area.

        Args:
            area:
                The name or partial name for the area to be returned. The matching of the area
                is done by matching the LSOA name. For example, passing area=Cambridge, will
                return LSOAs for Cambridge and Cambridgeshire

        Returns:
            Pandas dataframe with loaded LSOAs
        """
        if global_lsoa is None:
            global_lsoa = self.read_lsoa_objects_england()

        area_lsoa_pd = DataFrame(
            global_lsoa[global_lsoa[self.lsoa_name_col].str.contains(area)]
        )
        area_lsoa_pd.reset_index(drop=True, inplace=True)
        area_lsoa_pd[self.lsoa_object_id_col] = area_lsoa_pd[
            self.lsoa_object_id_col
        ].astype(int)
        area_lsoa_pd[self.lsoa_code_col] = area_lsoa_pd[self.lsoa_code_col].astype(str)

        return area_lsoa_pd

    def load_lsoa_population_estimates_england(
        self, area: str, global_lsoa_population_estimates: TextFileReader = None
    ) -> DataFrame:
        """
        Loads the LSOA population estimates for area in England.

        Args:
            area: The name or partial name for the area to be returned. The matching of the area
                is done by matching the LSOA name. For example, passing area=Cambridge, will
                return LSOAs for Cambridge and Cambridgeshire
            global_lsoa_population_estimates: Text file reader where the population can be loaded from. In case the file reader is None
                the LSOA will be loaded from default lsoa_popupation_data_path

        Returns:
            Pandas dataframe with loaded LSOAs and population
        """
        if global_lsoa_population_estimates is None:
            global_lsoa_population_estimates = (
                self.read_lsoa_population_estimates_england()
            )

        lsoa_population_estimates_pd = DataFrame(
            global_lsoa_population_estimates[
                global_lsoa_population_estimates[self.lsoa_name_col].str.contains(area)
            ]
        )
        lsoa_population_estimates_pd.reset_index(drop=True, inplace=True)
        lsoa_population_estimates_pd[self.lsoa_population_col] = (
            lsoa_population_estimates_pd[self.lsoa_population_col]
            .str.replace(",", "")
            .astype(int)
        )

        return lsoa_population_estimates_pd

    def build_lsoa_data_frame_for_area_england(self, area: str) -> DataFrame:
        """
        Loads and builds data frame containing information about LSOA and population
        for provided area in England.

        Args:
            area:
                The name or partial name for the area to be returned. The matching of the area
                is done by matching the LSOA name. For example, passing area=Cambridge, will
                return LSOAs for Cambridge and Cambridgeshire

        Returns:
             Pandas dataframe with loaded LSOAs and population
        """
        lsoa_df = self.load_lsoa_objects_for_area_england(area)
        lsoa_population_df = self.load_lsoa_population_estimates_england(area)
        # Dropping the duplicate column before the merge
        lsoa_population_df.drop(columns=[self.lsoa_name_col], inplace=True)

        lsoa_with_population_pd = pd.merge(
            lsoa_df,
            lsoa_population_df,
            left_on=self.lsoa_code_col,
            right_on=self.lsoa_code_col,
        )
        lsoa_with_population_pd[self.lsoa_object_id_col] = lsoa_with_population_pd[
            self.lsoa_object_id_col
        ].astype(str)

        return lsoa_with_population_pd

    def load_geo_json_shapefiles_for_lsoas(
        self, lsoas: DataFrame, area: str = None
    ) -> dict:
        """
        Loads geojson shape files for provided lsoas.

        Args:
            lsoas:
                Pandas dataframe containing object ids for all lsoas to load
            area:
                Area to filter lsoas by. The loading method split object ids
                to chunks to allow faster loading and prevent throttling from
                the geoportal. This means that it can load lsoas for areas
                outside of the area of interest. Providing area will ensure
                lsoas will be filtered by the area and only those will be returned.
        Returns:
            dictionary of all lsoas geojson keyed by the lsoa code
        """
        # Create split of objects to chunks
        object_ids_chunks = [[]]
        prev_objid = lsoas[self.lsoa_object_id_col].min()
        for _, row in lsoas.iterrows():
            current_objid = row[self.lsoa_object_id_col]
            if int(current_objid) - int(prev_objid) > 1:
                object_ids_chunks.append([])
            object_ids_chunks[-1].append(current_objid)
            prev_objid = current_objid

        # Load the LSOA geofiles from the arcgis and merge into one geogson file for processing
        # obtained via
        # https://geoportal.statistics.gov.uk/datasets/ons::lsoa-dec-2021-boundaries-full-clipped-ew-bfc/about
        lsoa_shapefile = None
        for chunk in object_ids_chunks:
            geo_json_url_link = f"https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LSOA_Dec_2021_Boundaries_Full_Clipped_EW_BFC_2022/FeatureServer/0/query?where=OBJECTID>={chunk[0]}%20AND%20OBJECTID<={chunk[-1]}&outFields=*&outSR=4326&f=geojson"
            lsoa_shapefile_r = urllib.request.urlopen(geo_json_url_link)
            lsoa_shapefile_all = geojson.loads(lsoa_shapefile_r.read())
            if lsoa_shapefile is not None:
                lsoa_shapefile["features"] = (
                    lsoa_shapefile_all["features"] + lsoa_shapefile["features"]
                )
            else:
                lsoa_shapefile = lsoa_shapefile_all

        # Return all loaded LSOAs if no further filtering is requested
        remapped_lsoa = copy.deepcopy(lsoa_shapefile)
        if area is None or area.strip() == "":
            return remapped_lsoa

        # Filter LSOAs from area only
        # Loading by OBJECTID could bring additional objects not in the area
        remapped_lsoa["features"] = []
        for feature in lsoa_shapefile["features"]:
            row_json = lsoas.loc[
                lsoas[self.lsoa_code_col] == feature["properties"][self.lsoa_code_col]
            ].to_dict(orient="records")
            if len(row_json):
                feature["properties"] = {**feature["properties"], **row_json[0]}
                remapped_lsoa["features"].append(copy.deepcopy(feature))

        return remapped_lsoa


def read_lsoa_objects_england(
    lsoa_data_path: str = None,
    object_id_col_number: int = 0,
    lsoa_code_col_number: int = 1,
    lsoa_name_col_number: int = 2,
    lsoa_global_id_col_number: int = 3,
) -> TextFileReader:
    """
    Reads the CSV file with lsoa data definitions.

    Args:
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

    Returns:
        Text file reader object which can be passed to pandas to create data frame
        or can be manipulated directly.
    """
    return LsoaLoader(
        definitions_data_path=lsoa_data_path,
        defs_object_id_col_number=object_id_col_number,
        defs_code_col_number=lsoa_code_col_number,
        defs_name_col_number=lsoa_name_col_number,
        defs_global_id_col_number=lsoa_global_id_col_number,
    ).read_lsoa_objects_england()


def read_lsoa_population_estimates_england(
    lsoa_data_path: str = None,
    skip_rows: int = 9,
    lsoa_code_col_number: int = 1,
    lsoa_name_col_number: int = 0,
    lsoa_population_col_number: int = 2,
) -> TextFileReader:
    """
    Read the CSV file with population figures from each LSOA.

    Args:
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

    Returns:
        Text file reader object with can be passed to pandas to create data frame
        or can be manipulated directly
    """
    loader = LsoaLoader(
        population_data_path=lsoa_data_path,
        population_skip_rows=skip_rows,
        population_code_col_number=lsoa_code_col_number,
        population_name_col_number=lsoa_name_col_number,
        population_population_col_number=lsoa_population_col_number,
    )
    return loader.read_lsoa_population_estimates_england()


def load_lsoa_objects_for_area_england(
    area: str, global_lsoa: TextFileReader = None
) -> DataFrame:
    """
    Loads lsoa object for england and returning data frame containing only LSOAs
    for the passed area.

    Args:
        area:
            The name or partial name for the area to be returned. The matching of the area
            is done by matching the LSOA name. For example, passing area=Cambridge, will
            return LSOAs for Cambridge and Cambridgeshire

    Returns:
        Pandas dataframe with loaded LSOAs
    """
    return LsoaLoader().load_lsoa_objects_for_area_england(
        area=area, global_lsoa=global_lsoa
    )


postcode_col = "POSTCODE"
lsoa_name_col = 2
lsoa_code_col = 1


def load_lsoa_objects_for_postcode_england(
    postcode: str,
    global_lsoa: TextFileReader = None,
    lsoa_postcode_map_file_path: str = lsoa_postcode_map_data_path,
    postcode_col_number: int = 0,
    lsoa_code_col_number: int = 1,
) -> DataFrame:
    """
    Loads lsoa based on specified postcode. Provided postcode is used as indicator for LSOAs
    names to be loaded. For example, if postcode belongs to Cambridge LSOAs, this function
    will load all Cambridge LSOAs. The usage is to provide postcode of medical facility and
    all surrounding LSOAs for this medical facility will be loaded.
    Parameters
    postcode:
        The postcode in England to map to LSOA name
    global_lsoa:
        Text file with all LSOAs for England
    lsoa_postcode_map_file_path:
        The file path with postcode to LSOA mapping
    postcode_col_number:
        The column number in the postcode to LSOA mapping file containing postcode
    lsoa_code_col_number:
        The column number in the postcode to LSOA mapping file containing LSOA code
    returns:
        Pandas dataframe with loaded LSOAs
    """
    if global_lsoa is None:
        global_lsoa = read_lsoa_objects_england()

    postcodes_map_df = pd.read_csv(
        lsoa_postcode_map_file_path,
        header=0,
        usecols=[postcode_col_number, lsoa_code_col_number],
        names=[postcode_col, lsoa_code_col],
        dtype="string",
    )
    postcodes_map_df = postcodes_map_df[
        postcodes_map_df[postcode_col].str.contains(postcode)
    ]
    postcodes_map_df.reset_index(drop=True, inplace=True)
    if postcodes_map_df.shape[0] == 0:
        raise ValueError(f"No postcode {postcode} found in the mapping file")

    lsoa_code = postcodes_map_df.at[0, lsoa_code_col]
    lsoa_name_df = global_lsoa[global_lsoa[lsoa_code_col].str.contains(lsoa_code)]
    lsoa_name_df.reset_index(drop=True, inplace=True)

    if lsoa_name_df.shape[0] == 0:
        raise ValueError(f"No lsoa with code {lsoa_code} found in global lsoas file")

    lsoa_name = lsoa_name_df.at[0, lsoa_name_col]
    lsoa_area = "".join(lsoa_name.split()[:-1])
    return load_lsoa_objects_for_area_england(lsoa_area, global_lsoa)


def load_lsoa_population_estimates_england(
    area: str, global_lsoa_population_estimates: TextFileReader = None
) -> DataFrame:
    """
    Loads the LSOA population estimates for area in England.

    Args:
        area:
            The name or partial name for the area to be returned. The matching of the area
            is done by matching the LSOA name. For example, passing area=Cambridge, will
            return LSOAs for Cambridge and Cambridgeshire
        global_lsoa_population_estimates:
            Text file reader where the population can be loaded from. In case the file reader is None
            the LSOA will be loaded from default lsoa_popupation_data_path

    Returns:
        Pandas dataframe with loaded LSOAs and population
    """
    loader = LsoaLoader()
    return loader.load_lsoa_population_estimates_england(
        area=area, global_lsoa_population_estimates=global_lsoa_population_estimates
    )


def build_lsoa_data_frame_for_area_england(area: str) -> DataFrame:
    """
    Loads and builds data frame containing information about LSOA and population
    for provided area in England.

    Args:
        area:
            The name or partial name for the area to be returned. The matching of the area
            is done by matching the LSOA name. For example, passing area=Cambridge, will
            return LSOAs for Cambridge and Cambridgeshire

    Returns:
         Pandas dataframe with loaded LSOAs and population
    """
    return LsoaLoader().build_lsoa_data_frame_for_area_england(area=area)


def load_geo_json_shapefiles_for_lsoas(lsoas: DataFrame, area: str = None) -> dict:
    """
    Loads geojson shape files for provided LSOAs

    Args:
        lsoas: Pandas dataframe containing object ids for all lsoas to load
        area: Area to filter lsoas by. The loading method split object ids
            to chunks to allow faster loading and prevent throttling from
            the geoportal. This means that it can load lsoas for areas
            outside of the area of interest. Providing area will ensure
            lsoas will be filtered by the area and only those will be returned.

    Returns:
        dictionary of all lsoas geojson keyed by the lsoa code
    """
    return LsoaLoader().load_geo_json_shapefiles_for_lsoas(lsoas=lsoas, area=area)
