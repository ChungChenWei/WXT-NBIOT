from ftplib import FTP
from path_config import RAW_PATH
from ftp_config import FTP_IP, USER_NAME, USER_PASS

ftp = FTP(FTP_IP)
ftp.login(USER_NAME, USER_PASS)

log_files = ftp.nlst()

print(log_files)

for file_name in log_files:
    with open(RAW_PATH / file_name, "wb") as fo:
        ftp.retrbinary(f"RETR {file_name}", fo.write)

ftp.quit()
