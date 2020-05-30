#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 30 May 2020

import logging
import os.path
import sys

from um7py.um7_serial import UM7Serial


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='[%(asctime)s.%(msecs)03d] [%(levelname)-8s]:  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(f'{os.path.basename(__file__)}.log'),
            logging.StreamHandler(sys.stdout),
        ])
    script_dir = os.path.dirname(__file__)
    device_file = os.path.join(script_dir, os.pardir, "um7_A500CNP8.json")
    um7 = UM7Serial(device=device_file)
    print("Below are collection of commands, running these commands might erase your settings."
          " Only do it if you are sure of what you are doing.")
    know_what_will_happen = False
    if not know_what_will_happen:
        print("NO commands will be executed, Get firmware revision and exit. All fine."
              " To execute the commands change the `know_what_will_happen` to `True` and select commands you need.")
        print(f"get_fw_revision               : {um7.get_fw_revision}")
    else:
        print(f"\\n========== COMMAND REGISTERS ===================================")
        print(f"get_fw_revision               : {um7.get_fw_revision}")
        print(f"flash_commit                  : {um7.flash_commit}")
        print(f"reset_to_factory              : {um7.reset_to_factory}")
        print(f"zero_gyros                    : {um7.zero_gyros}")
        print(f"set_home_position             : {um7.set_home_position}")
        print(f"set_mag_reference             : {um7.set_mag_reference}")
        print(f"calibrate_accelerometers      : {um7.calibrate_accelerometers}")
        print(f"reset_ekf                     : {um7.reset_ekf}")

