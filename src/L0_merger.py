from datetime import datetime as dtmdtm
from pathlib import Path
from typing import List

import pandas as pd

from config.path_config import MERGE_PATH, L0_PATH, mkdir_if_not_exist
from utils import dump_hash, get_files_md5, load_hash


def merge(files: List[Path]):
    dfs: pd.DataFrame = None
    for file in files:
        df = pd.read_csv(file, index_col="datetime")
        if dfs is None:
            dfs = df
        else:
            dfs = pd.concat([dfs, df]).drop_duplicates()
    return dfs.sort_index()


if __name__ == "__main__":
    utc = dtmdtm.now()
    series = pd.date_range("20230412", dtmdtm.now())
    targets = [t.strftime("%Y%m%d") for t in series]

    for target_date in targets:
        OUTPUT = MERGE_PATH / target_date
        mkdir_if_not_exist(OUTPUT)

        file_dict = {}
        for file in L0_PATH.rglob(f"{target_date}*.csv"):
            station = file.parent.name
            file_list = file_dict.get(station, [])
            file_list.append(file)
            file_dict[station] = file_list
        for station, files in file_dict.items():
            hash = load_hash(station, type="merge")
            currnt_md5_hash = get_files_md5(files)
            old_md5_hash = hash.get(target_date, "")
            if old_md5_hash == currnt_md5_hash:
                continue

            df = merge(files)
            df.to_csv(OUTPUT / f"{station}.csv")

            hash[target_date] = currnt_md5_hash
            print(station, target_date, "updated")

            dump_hash(hash, station, type="merge")
