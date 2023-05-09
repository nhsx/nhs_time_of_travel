import unittest
import pandas as pd
from scripts.tsp import *
from functions.tsp_functions import *


class TestTSPfunctions(unittest.TestCase):
    def test_get_coords_address_using_latlong(self):
        # Construct dataframe and
        df = pd.DataFrame(
            [
                {
                    "Address": "Oaks Place, Mile End Road, Colchester",
                    "Latitude": 51.9063,
                    "Longitude": 0.8950,
                },
                {
                    "Address": "Turner Road, Colchester",
                    "Latitude": 51.9102,
                    "Longitude": 0.8992,
                },
            ]
        )

        coords, addresses = get_coords_addresses(df, geolocator=None)
        permutations = create_permutations(
            coords, addresses, first_address="Oaks Place, Mile End Road, Colchester"
        )
