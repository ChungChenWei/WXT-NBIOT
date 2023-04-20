from ftplib import FTP
from config.path_config import RAW_PATH
from config.ftp_config import FTP_IP, USER_NAME, USER_PASS
from datetime import datetime as dtmdtm, timedelta as dt

ftp = FTP(FTP_IP)
ftp.login(USER_NAME, USER_PASS)

log_files = ftp.nlst()

print(log_files)

for file_name in log_files:
    utc = dtmdtm.utcnow()
    target = [(utc - dt(minutes=10)).strftime("%m%d"), utc.strftime("%m%d")]
    if target[0] in file_name or target[1] in file_name:
        with open(RAW_PATH / file_name, "wb") as fo:
            ftp.retrbinary(f"RETR {file_name}", fo.write)
        with open(RAW_PATH / ".." / "ftp.txt", "w") as fo:
            fo.write(dtmdtm.now().strftime("%Y/%m/%d %H:%M:%S"))

ftp.quit()
