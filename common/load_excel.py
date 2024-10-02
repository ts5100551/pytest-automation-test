import os


import pandas as pd
import yaml

map_table = {
    "test1": "Test1API_TestData.xlsx",
    "test2": "Test2API_TestData.xlsx",
}


def load_env() -> str:
    config_path = os.path.join("configurations", "config.yaml")
    with open(config_path) as f:
        d = yaml.load(f.read(), Loader=yaml.SafeLoader)
        env = d["Env"]
    return env


def load_data(
    site: str, api_id: str, performance_api_name: str = None, functional_api_name=None
) -> list:
    env = load_env()
    df = pd.read_excel(f"testdata/env-{env}/{map_table[site]}", dtype=str)
    df = df.dropna(how="all")
    df_target = df.loc[df["api_id"] == api_id]

    data = []
    for i in df_target.values:  # i 為每一行的value的列表：[a2, b2, c2, d2]
        data.append(tuple(i))

    return data


def load_ids(
    site: str, api_id: str, performance_api_name: str = None, functional_api_name=None
) -> list:
    env = load_env()

    df = pd.read_excel(f"testdata/env-{env}/{map_table[site]}")
    df = df.dropna(how="all")
    df_target = df.loc[df["api_id"] == api_id]

    ids = []
    for i in df_target["case_id"].values:
        ids.append(i)

    return ids
