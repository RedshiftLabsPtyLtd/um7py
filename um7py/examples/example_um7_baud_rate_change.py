#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 08 August 2020


import logging
import os.path
import sys

from um7py.um7_serial import UM7Serial
from um7py.rsl_xml_svd.rsl_svd_parser import Register


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='[%(asctime)s.%(msecs)03d]: %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(f'{os.path.basename(__file__)}.log', mode='w'),
            logging.StreamHandler(sys.stdout),
        ])
    um7 = UM7Serial(port_name='/dev/ttyUSB0')

    print("um7 firmware revision: {}".format(um7.get_fw_revision))
    creg_com_settings = um7.creg_com_settings

    # for packet in um7.recv_broadcast(num_packets=1000):
    #     logging.warning(packet)

