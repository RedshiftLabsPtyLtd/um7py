#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 29 May 2020
# Example: reading broadcast packet of processed sensor data

import logging
import os.path
import sys

from um7py.um7_serial import UM7Serial


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='[%(asctime)s.%(msecs)03d]: %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(f'{os.path.basename(__file__)}.log', mode='w'),
            logging.StreamHandler(sys.stdout),
        ])
    script_dir = os.path.dirname(__file__)
    device_file = os.path.join(script_dir, os.pardir, "um7_A500CNP8.json")
    um7 = UM7Serial(device=device_file)

    flush_on_start = True  # <-- optional, set to true if you want to reset input buffer when starting reception
    for packet in um7.recv_all_proc_broadcast(num_packets=10000, flush_buffer_on_start=flush_on_start):
        logging.warning(packet)
