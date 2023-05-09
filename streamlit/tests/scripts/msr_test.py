import unittest
import pandas as pd
from scripts.msr import *


class TestMSR(unittest.TestCase):
    def test_get_long_lat_from_df(self):
        # Construct dataframe and
        df = pd.DataFrame([{"Latitude": 52, "Longitude": 0}])
        result = get_lat_long(True, df.iloc[0, :])
        self.assertEqual(result, (52, 0))

    def test_get_long_lat_from_address(self):
        # Construct dataframe and
        df = pd.DataFrame([{"Address": "Oriental Road, Woking"}])
        result = get_lat_long(False, df.iloc[0, :])
        self.assertEqual(result, (51.3178181, -0.556127))

    def test_travel_times(self):
        df = pd.DataFrame([{"Name": "foo", "Address": "untouched Address"}])
        distance_in_miles = [75]

        result = travel_times(df, distance_in_miles)
        expected_result = pd.DataFrame(
            [
                {
                    "Name": "foo",
                    "Address": "untouched Address",
                    "Distance in Miles": 75,
                    "Walking time (min)": 25 * 60.0,
                    "Peak driving time (min)": 300.0,
                    "Off-peak driving time (min)": 180.0,
                }
            ]
        )
        pd.testing.assert_frame_equal(result, expected_result)

    def test_travel_times_rounding(self):
        df = pd.DataFrame([{"Name": "foo", "Address": "untouched Address"}])
        distance_in_miles = [1.12345]

        result = travel_times(df, distance_in_miles)

        # Times should use rounded values for consistency
        expected_result = pd.DataFrame(
            [
                {
                    "Name": "foo",
                    "Address": "untouched Address",
                    "Distance in Miles": 1.12,
                    "Walking time (min)": (1.12 / 3) * 60.0,
                    "Peak driving time (min)": (1.12 / 15) * 60,
                    "Off-peak driving time (min)": (1.12 / 25) * 60,
                }
            ]
        )
        pd.testing.assert_frame_equal(result, expected_result)


if __name__ == "__main__":
    unittest.main()
