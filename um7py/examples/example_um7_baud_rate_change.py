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
    # um7.port.close()
    # um7.port.baudrate = 38400
    # um7.port.open()
    # um7.connect()

    print("um7 firmware revision: {}".format(um7.get_fw_revision))
    creg_com_settings, *_ = um7.creg_com_settings
    print("um7 creg_com_settings: {}".format(um7.creg_com_settings))

    print(f"setting new baud rate: ...")
    # look at the register description -->
    # http://rsl.selyunin.com/register_map_current.html#creg-com-settings
    # 3 of BAUD_RATE corresponds to the 57600 BAUD
    creg_com_settings.set_field_value(BAUD_RATE=4)
    # we have now set a raw register value, let us write it in the sensor
    um7.creg_com_settings = creg_com_settings.raw_value

    # let us update the baud rate of the communication object:
    from time import sleep
    sleep(2)
    um7.port.close()
    um7.port.baudrate = 57600
    um7.port.open()
    # let us try to read out firmware revision now, with the new rate:
    print("um7 firmware revision: {}".format(um7.get_fw_revision))

    # let us restore baud rate back to 115200
    print(f"Setting baud rate back to 115200")
    # creg_com_settings.set_field_value(BAUD_RATE=5)
    # um7.creg_com_settings = creg_com_settings.raw_value

    sleep(1)

    # for packet in um7.recv_broadcast(num_packets=10):
    #     logging.warning(packet)

