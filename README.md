# WXT-NBIOT

## 流程

- `download.py`
- `spliter.py`

## 說明

### `download.py`

- 從 C302.5 的資料蒐集電腦中，以 FTP 的方式獲取記錄檔。
- 需要搭配 `ftp_config.py` 設定 `ip` 與帳號密碼。
- 格式請參考 `ftp_config.example.py` 並於設定完成後複製更名為 `ftp_config.py`。

### `spliter.py`

- 將原始資料以日期與站名拆解。