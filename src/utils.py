import json
from hashlib import md5
from pathlib import Path
from typing import List

from config.path_config import HASH_PATH


def load_hash(mode: str, type: str):
    try:
        with open(HASH_PATH / f"{type}_{mode}_hash.json", "r") as fi:
            return json.load(fi)
    except FileNotFoundError:
        return {}


def dump_hash(hash: dict, mode: str, type: str):
    with open(HASH_PATH / f"{type}_{mode}_hash.json", "w") as fo:
        json.dump(hash, fo, indent=2)


def get_file_md5(filename):
    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_files_md5(files: List[Path]):
    hash_md5 = md5()
    for file in files:
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    return hash_md5.hexdigest()
