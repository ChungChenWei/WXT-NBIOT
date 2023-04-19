from pathlib import Path

ROOT_DIR = Path("..")
DATA_DIR = ROOT_DIR / "data"

RAW_PATH = DATA_DIR / "raw"
L0_PATH = DATA_DIR / "L0"


def mkdir_if_not_exist(path: Path):
    if not path.exists():
        path.mkdir(parents=True)


mkdir_if_not_exist(RAW_PATH)
mkdir_if_not_exist(L0_PATH)
