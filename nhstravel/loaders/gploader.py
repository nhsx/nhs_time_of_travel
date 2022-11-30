import pandas as pd


def load(gp_data_path='data/gp_data.csv'):
    return pd.read_csv(gp_data_path)
