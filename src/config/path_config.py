from pathlib import Path

ROOT_DIR = Path("..")
DATA_DIR = ROOT_DIR / "data"
PICT_DIR = ROOT_DIR / "pic"

RAW_PATH = DATA_DIR / "raw"
L0_PATH = DATA_DIR / "L0"
MERGE_PATH = DATA_DIR / "merge"
HASH_PATH = DATA_DIR / "hash"

FTP_PATH = RAW_PATH / "ftp"
SD_PATH = RAW_PATH / "sd"


def mkdir_if_not_exist(path: Path):
    if not path.exists():
        path.mkdir(parents=True)


mkdir_if_not_exist(RAW_PATH)
mkdir_if_not_exist(PICT_DIR)
mkdir_if_not_exist(L0_PATH)
mkdir_if_not_exist(MERGE_PATH)
mkdir_if_not_exist(HASH_PATH)
mkdir_if_not_exist(FTP_PATH)
mkdir_if_not_exist(SD_PATH)
