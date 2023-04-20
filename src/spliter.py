import json
from datetime import datetime as dtmdtm
from hashlib import md5

import pandas as pd

from config.path_config import DATA_DIR, L0_PATH, RAW_PATH, mkdir_if_not_exist

idx_start = 3  # position of data start in a line
idx_end = -5
cycle_int = 4
idx_time = 0
idx_station = -3


def main(file_path):
    date = dtmdtm.strptime(file_path.stem, "%Y%m%dERR")

    df = pd.DataFrame(columns=["station", "datetime"])
    with open(file_path) as fi:
        lines = fi.readlines()
        for line in lines:
            if not check_line_valid(line):
                continue

            splits = line.strip().split(",")

            data = splits[idx_start:idx_end]
            record = dataset_processor(data)
            if len(record) == 0:
                continue

            time = splits[idx_time]
            try:
                time = dtmdtm.strptime(time, "%H:%M:%S")
            except ValueError:
                print(f"ERROR in {line}")
                continue
            station_name = splits[idx_station]
            datetime = dtmdtm.combine(date.date(), time.time())

            record = {"station": station_name, "datetime": datetime, **record}
            df = df.append(record, ignore_index=True)
        df = df.set_index("datetime")
        to_split_station_L0(df)


def check_line_valid(line: str):
    if "noETX" not in line:
        return False
    if "Server" in line:
        return False
    splits = line.strip().split(",")
    if len(splits) < (abs(idx_start) + abs(idx_end)):
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


def to_split_station_L0(df: pd.DataFrame):
    dfg = df.groupby("station")
    for name, data in dfg:
        data.dropna(axis=1, how="all", inplace=True)
        datetime = data.index[0]
        OUTPUT_PATH = L0_PATH / datetime.strftime("%Y%m%d")
        mkdir_if_not_exist(OUTPUT_PATH)
        try:
            data.to_csv(OUTPUT_PATH / f"{name}.csv")
        except OSError as e:
            print(e)


def get_file_md5(filename):
    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    try:
        with open(DATA_DIR / "raw_hash.json", "r") as fi:
            hash = json.load(fi)
    except FileNotFoundError:
        hash = {}

    for file in RAW_PATH.glob("*.LOG"):
        currnt_md5_hash = get_file_md5(file)
        old_md5_hash = hash.get(file.name, "")
        if old_md5_hash != currnt_md5_hash:
            print(file.name)
            main(file)
            hash[file.name] = currnt_md5_hash
            print(file.name, "updated")

        with open(DATA_DIR / "raw_hash.json", "w") as fo:
            json.dump(hash, fo, indent=2)
