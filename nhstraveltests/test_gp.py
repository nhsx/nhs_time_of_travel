import unittest

import pandas as pd
from shapely.geometry import Point, Polygon
from nhstravel.gp import GpRegion


class MyTestCase(unittest.TestCase):
    def test_gp_find_practices(self):
        area = GpRegion.load_england()
        botley_df = area.find_practices("botley")
        # For this test assume there is a single practice with "Botley" in the name,
        # and the location. This may break in future.
        self.assertEqual(1, len(botley_df.index))
        botley_location = botley_df.iloc[0]["point"]
        self.assertEqual(botley_location, Point(-1.2983483, 51.7527945))

    def test_get_practice_area(self):
        data = {
            "Name": ["TOP", "LEFT", "RIGHT", "MIDDLE"],
            "latitude": [51.52, 51.50, 51.50, 51.51],
            "longitude": [-0.085, -0.095, -0.080, -0.085],
            "Postcode": [
                "",
                "",
                "",
                "",
            ],
            "National Grouping": [
                "",
                "",
                "",
                "",
            ],
            "High Level Health Geography": [
                "",
                "",
                "",
                "",
            ],
        }
        area = GpRegion._from_df(pd.DataFrame(data))
        middle_df = area.find_practices("middle")
        botley_area = area.get_practice_area(middle_df.index[0])

        expected = Polygon(
            [
                Point(-0.080, 51.50),
                Point(-0.095, 51.50),
                Point(-0.085, 51.52),
                Point(-0.080, 51.50),
            ]
        )
        self.assertEqual(str(botley_area.area), str(expected))


if __name__ == "__main__":
    unittest.main()
