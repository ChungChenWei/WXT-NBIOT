import os
import zipfile

import dropbox
from dotenv import load_dotenv

from config.path_config import DATA_DIR, SD_PATH

load_dotenv()

dbx = dropbox.Dropbox(os.environ["DROPBOX_TOKEN"])
shared_link = "https://www.dropbox.com/scl/fo/zgpu9k1gs8xg70agdq5h4/h?dl=0&rlkey=11qqs6b5utghzgpjy1m8fyoqx"

# 取得共享檔案的資訊
link_info = dbx.sharing_get_shared_link_metadata(shared_link)

print(link_info.name)

ZIP_PATH = DATA_DIR / f"{link_info.name}.zip"

dbx.files_download_zip_to_file(ZIP_PATH, link_info.path_lower)

with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
    zip_ref.extractall(SD_PATH)
