#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 29 May 2020

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
    print(f"\\n========== CONFIG REGISTERS ===================================")
    print(f"creg_com_settings             : {um7.creg_com_settings}")
    print(f"creg_com_rates1               : {um7.creg_com_rates1}")
    print(f"creg_com_rates2               : {um7.creg_com_rates2}")
    print(f"creg_com_rates3               : {um7.creg_com_rates3}")
    print(f"creg_com_rates4               : {um7.creg_com_rates4}")
    print(f"creg_com_rates5               : {um7.creg_com_rates5}")
    print(f"creg_com_rates6               : {um7.creg_com_rates6}")
    print(f"creg_com_rates7               : {um7.creg_com_rates7}")
    print(f"creg_misc_settings            : {um7.creg_misc_settings}")
    print(f"creg_home_north               : {um7.creg_home_north}")
    print(f"creg_home_east                : {um7.creg_home_east}")
    print(f"creg_home_up                  : {um7.creg_home_up}")
    print(f"creg_gyro_trim_x              : {um7.creg_gyro_trim_x}")
    print(f"creg_gyro_trim_y              : {um7.creg_gyro_trim_y}")
    print(f"creg_gyro_trim_z              : {um7.creg_gyro_trim_z}")
    print(f"creg_mag_cal1_1               : {um7.creg_mag_cal1_1}")
    print(f"creg_mag_1_cal1_2             : {um7.creg_mag_1_cal1_2}")
    print(f"creg_mag_cal1_3               : {um7.creg_mag_cal1_3}")
    print(f"creg_mag_cal2_1               : {um7.creg_mag_cal2_1}")
    print(f"creg_mag_cal2_2               : {um7.creg_mag_cal2_2}")
    print(f"creg_mag_cal2_3               : {um7.creg_mag_cal2_3}")
    print(f"creg_mag_cal3_1               : {um7.creg_mag_cal3_1}")
    print(f"creg_mag_cal3_2               : {um7.creg_mag_cal3_2}")
    print(f"creg_mag_cal3_3               : {um7.creg_mag_cal3_3}")
    print(f"creg_mag_bias_x               : {um7.creg_mag_bias_x}")
    print(f"creg_mag_1_bias_y             : {um7.creg_mag_1_bias_y}")
    print(f"creg_mag_bias_z               : {um7.creg_mag_bias_z}")
    print(f"creg_accel_cal1_1             : {um7.creg_accel_cal1_1}")
    print(f"creg_accel_cal1_2             : {um7.creg_accel_cal1_2}")
    print(f"creg_accel_cal1_3             : {um7.creg_accel_cal1_3}")
    print(f"creg_accel_cal2_1             : {um7.creg_accel_cal2_1}")
    print(f"creg_accel_cal2_2             : {um7.creg_accel_cal2_2}")
    print(f"creg_accel_cal2_3             : {um7.creg_accel_cal2_3}")
    print(f"creg_accel_cal3_1             : {um7.creg_accel_cal3_1}")
    print(f"creg_accel_cal3_2             : {um7.creg_accel_cal3_2}")
    print(f"creg_accel_cal3_3             : {um7.creg_accel_cal3_3}")
    print(f"creg_accel_bias_x             : {um7.creg_accel_bias_x}")
    print(f"creg_accel_bias_y             : {um7.creg_accel_bias_y}")
    print(f"creg_accel_bias_z             : {um7.creg_accel_bias_z}")
