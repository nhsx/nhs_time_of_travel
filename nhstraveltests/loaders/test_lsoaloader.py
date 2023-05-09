import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from nhstravel.loaders.lsoaloader import (
    read_lsoa_objects_england,
    load_lsoa_objects_for_area_england,
)


class MyTestCase(unittest.TestCase):
    def test_read_lsoa_objects_england(self):
        reader = read_lsoa_objects_england()
        objects = load_lsoa_objects_for_area_england("Cambridge", reader)
        self.assertEqual(228, len(objects))
        expected = pd.DataFrame.from_dict(
            {
                "OBJECTID": pd.Series(17032),
                "LSOA21CD": pd.Series("E01017943", dtype="object"),
                "LSOA21NM": pd.Series("Cambridge 006A", dtype="string"),
                "GlobalID": pd.Series(
                    "5DAF269C-8A7B-48BF-A941-5F56F36D53A7", dtype="string"
                ),
            }
        )
        assert_frame_equal(objects.iloc[[0]], expected)


if __name__ == "__main__":
    unittest.main()
