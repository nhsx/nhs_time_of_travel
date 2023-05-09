import pandas as pd


def load(gp_data_path="data/gp_data.csv"):
    return pd.read_csv(gp_data_path)


def load_england(
    gp_data_path="data/gp_data.csv",
    only_england_grouping=True,
    only_gp=True,
    only_active=True,
):
    """
    Load data for all GP services in England. Some default filters are applied to remove
    likely unwanted data, but these can be configured
    :param gp_data_path:
    :param only_england_grouping: In the eppracur.pdf spec it gives a National Grouping which can exclude Welsh and
        Channel Island practices. If True (default) then practices with non english codes are excluded
    :param only_gp: In Eppracur column 26, prescribing setting gives the type of setting. If true only prescribing
        settings which are GP Practice (1,2,3 or 4) are included
    :param only_active: In Eppracur column 13 there is a status code which indicates if the GP is active. If True
        (default) only includes active, and excludes closed, dormant or proposed
    :return:
    """
    df = pd.read_csv(gp_data_path)
    if only_england_grouping:
        df = df[
            df["National Grouping"].isin(
                ["Y63", "Y62", "Y60", "Y61", "Y56", "Y59", "Y58"]
            )
        ]
    if only_gp:
        df = df[df["Prescribing Setting"].isin([1, 2, 3, 4])]
    if only_active:
        df = df[df["Status Code"].isin(["A"])]
    return df
