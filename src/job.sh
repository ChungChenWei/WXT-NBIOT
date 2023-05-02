#!/bin/bash

/home/b07209016/anaconda3/bin/python /home/b07209016/WXT-NBIOT/WXT-NBIOT/src/download.py
/home/b07209016/anaconda3/bin/python /home/b07209016/WXT-NBIOT/WXT-NBIOT/src/raw_parser.py ftp
/home/b07209016/anaconda3/bin/python /home/b07209016/WXT-NBIOT/WXT-NBIOT/src/raw_parser.py sd
/home/b07209016/anaconda3/bin/python /home/b07209016/WXT-NBIOT/WXT-NBIOT/src/L0_merger.py
/home/b07209016/anaconda3/bin/python /home/b07209016/WXT-NBIOT/WXT-NBIOT/src/plotter.py
