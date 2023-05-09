import unittest
import pandas as pd
from scripts.tsp import *


class TestTSP(unittest.TestCase):
    def test_get_coords_address_using_latlong(self):
        # Construct dataframe and
        df = pd.DataFrame(
            [
                {
                    "Address": "Turner Road, Colchester",
                    "Latitude": 51.9102,
                    "Longitude": 0.8992,
                },
                {
                    "Address": "Oaks Place, Mile End Road, Colchester",
                    "Latitude": 51.9063,
                    "Longitude": 0.8950,
                },
            ]
        )

        coords, addresses = get_coords_addresses(df, geolocator=None)

        self.assertEqual(coords, [(51.9102, 0.8992), (51.9063, 0.8950)])

        self.assertEqual(
            addresses,
            ["Turner Road, Colchester", "Oaks Place, Mile End Road, Colchester"],
        )
