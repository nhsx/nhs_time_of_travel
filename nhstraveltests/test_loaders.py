# -*- coding: utf-8 -*-

from nhstravel.loaders import gploader

import os
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class LoadersTestSuite(unittest.TestCase):

    def test_gploader_load(self):
        df = gploader.load(gp_data_path=os.path.join(THIS_DIR, 'gp_file.csv'))
        assert len(df.columns) == 30


if __name__ == '__main__':
    unittest.main()
