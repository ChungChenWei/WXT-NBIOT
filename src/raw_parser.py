import json
import sys
from datetime import datetime as dtmdtm
from functools import partial
from hashlib import md5
from pathlib import Path

import pandas as pd

from config.path_config import DATA_DIR, L0_PATH, RAW_PATH, mkdir_if_not_exist

FTP_IDX = {
    "data_start": 3,
    "data_end": -5,
    "station_idx": -3,
}

SD_IDX = {
    "data_start": 1,
    "data_end": -5,
    "station_idx": -3,
}

IDX = {"ftp": FTP_IDX, "sd": SD_IDX}


def line_parser(line: str, data_start: int, data_end: int, station_idx: int):
    splits = line.strip().split(",")
    if len(splits) < (abs(data_start) + abs(data_end)):
        return {}

    data = splits[data_start:data_end]
    record = dataset_processor(data)
    if len(record) == 0:
        return {}

    try:
        datetime = "20" + "".join(splits[-5:-3])
        datetime = dtmdtm.strptime(datetime, "%Y%m%d%H%M%S")
    except ValueError:
        print(f"ERROR in {line}")
        return {}

    station_name = splits[station_idx]

    return {"station": station_name, "datetime": datetime, **record}


def parser(file_path: Path, mode: str):
    with open(file_path) as fi:
        lines = filter(check_line_valid, fi.readlines())
        records = list(map(partial(line_parser, **IDX[mode]), lines))
        df = pd.DataFrame(records)
        df.set_index("datetime", inplace=True)

    to_split_station_L0(df, L0_PATH / mode)


def check_line_valid(line: str):
    if "WIXDR" not in line:
        return False
    if "Server" in line:
        return False
    return True


def dataset_processor(data):
    record = {}
    for dataset in [data[i : i + 4] for i in range(0, len(data), 4)]:
        if "#" in dataset or len(dataset) != 4:
            continue
        val = dataset.pop(1)
        key = "".join(dataset)
        record[key] = val
    return record


def to_split_station_L0(df: pd.DataFrame, target: Path):
    dfg = df.groupby("station")
    for name, station_data in dfg:
        station_data.dropna(axis=1, how="all", inplace=True)
        OUTPUT_PATH = target / name
        try:
            mkdir_if_not_exist(OUTPUT_PATH)
        except OSError:  # some station error
            continue
        dfg = station_data.groupby(pd.Grouper(freq="D"))
        for name, day_data in dfg:
            datetime = day_data.index[0]
            try:
                day_data.to_csv(OUTPUT_PATH / f'{datetime.strftime("%Y%m%d%H%M")}.csv')
            except OSError as e:
                print(e)


def get_file_md5(filename):
    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_files(mode: str, filter="*"):
    return list((RAW_PATH / mode).rglob(filter))


def load_hash(mode: str):
    try:
        with open(DATA_DIR / f"raw_{mode}_hash.json", "r") as fi:
            return json.load(fi)
    except FileNotFoundError:
        return {}


def dump_hash(hash: dict, mode: str):
    with open(DATA_DIR / f"raw_{mode}_hash.json", "w") as fo:
        json.dump(hash, fo, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "ftp"

    if mode == "ftp":
        files = get_files("ftp", "*.LOG")
    elif mode == "sd":
        files = get_files("sd", "*.TXT")
    else:
        print("Mode not found")
        exit()

    hash = load_hash(mode)
    for file in files:
        hash_idx = f"{file.parent.name}{file.name}"

        currnt_md5_hash = get_file_md5(file)
        old_md5_hash = hash.get(hash_idx, "")
        if old_md5_hash == currnt_md5_hash:
            continue

        parser(file, mode)
        hash[hash_idx] = currnt_md5_hash
        print(hash_idx, "updated")

        dump_hash(hash, mode)
