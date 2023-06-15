# WXT-NBIOT

## 流程

- `download.py`
- `raw_parser.py`
- `L0_merger.py`
- `plotter.py`

## 說明

### `download.py`

- 從 C302.5 的資料蒐集電腦中，以 FTP 的方式獲取記錄檔。
- 需要搭配 `ftp_config.py` 設定 `ip` 與帳號密碼。
- 格式請參考 `ftp_config.example.py` 並於設定完成後複製更名為 `ftp_config.py`。

### `raw_parser.py`

- 將原始資料以日期與站名拆解。

### `L0_merger.py`

- 將 `ftp` 與 `sd` 資料進行合併

### `plotter.py`

- 繪圖
