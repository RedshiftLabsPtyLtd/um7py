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

    print(f"\\n========== DATA REGISTERS ===================================")
    print(f"dreg_health                   : {um7.dreg_health}")
    print(f"dreg_gyro_raw_xy              : {um7.dreg_gyro_raw_xy}")
    print(f"dreg_gyro_raw_z               : {um7.dreg_gyro_raw_z}")
    print(f"dreg_gyro_raw_time            : {um7.dreg_gyro_raw_time}")
    print(f"dreg_accel_raw_xy             : {um7.dreg_accel_raw_xy}")
    print(f"dreg_accel_raw_z              : {um7.dreg_accel_raw_z}")
    print(f"dreg_accel_raw_time           : {um7.dreg_accel_raw_time}")
    print(f"dreg_mag_raw_xy               : {um7.dreg_mag_raw_xy}")
    print(f"dreg_mag_raw_z                : {um7.dreg_mag_raw_z}")
    print(f"dreg_mag_raw_time             : {um7.dreg_mag_raw_time}")
    print(f"dreg_temperature              : {um7.dreg_temperature}")
    print(f"dreg_temperature_time         : {um7.dreg_temperature_time}")
    print(f"dreg_gyro_proc_x              : {um7.dreg_gyro_proc_x}")
    print(f"dreg_gyro_proc_y              : {um7.dreg_gyro_proc_y}")
    print(f"dreg_gyro_proc_z              : {um7.dreg_gyro_proc_z}")
    print(f"dreg_gyro_proc_time           : {um7.dreg_gyro_proc_time}")
    print(f"dreg_accel_proc_x             : {um7.dreg_accel_proc_x}")
    print(f"dreg_accel_proc_y             : {um7.dreg_accel_proc_y}")
    print(f"dreg_accel_proc_z             : {um7.dreg_accel_proc_z}")
    print(f"dreg_accel_proc_time          : {um7.dreg_accel_proc_time}")
    print(f"dreg_mag_proc_x               : {um7.dreg_mag_proc_x}")
    print(f"dreg_mag_proc_y               : {um7.dreg_mag_proc_y}")
    print(f"dreg_mag_proc_z               : {um7.dreg_mag_proc_z}")
    print(f"dreg_mag_proc_time            : {um7.dreg_mag_proc_time}")
    print(f"dreg_quat_ab                  : {um7.dreg_quat_ab}")
    print(f"dreg_quat_cd                  : {um7.dreg_quat_cd}")
    print(f"dreg_quat_time                : {um7.dreg_quat_time}")
    print(f"dreg_euler_phi_theta          : {um7.dreg_euler_phi_theta}")
    print(f"dreg_euler_psi                : {um7.dreg_euler_psi}")
    print(f"dreg_euler_phi_theta_dot      : {um7.dreg_euler_phi_theta_dot}")
    print(f"dreg_euler_psi_dot            : {um7.dreg_euler_psi_dot}")
    print(f"dreg_euler_time               : {um7.dreg_euler_time}")
    print(f"dreg_position_north           : {um7.dreg_position_north}")
    print(f"dreg_position_east            : {um7.dreg_position_east}")
    print(f"dreg_position_up              : {um7.dreg_position_up}")
    print(f"dreg_position_time            : {um7.dreg_position_time}")
    print(f"dreg_velocity_north           : {um7.dreg_velocity_north}")
    print(f"dreg_velocity_east            : {um7.dreg_velocity_east}")
    print(f"dreg_velocity_up              : {um7.dreg_velocity_up}")
    print(f"dreg_velocity_time            : {um7.dreg_velocity_time}")
    print(f"dreg_gps_latitude             : {um7.dreg_gps_latitude}")
    print(f"dreg_gps_longitude            : {um7.dreg_gps_longitude}")
    print(f"dreg_gps_altitude             : {um7.dreg_gps_altitude}")
    print(f"dreg_gps_course               : {um7.dreg_gps_course}")
    print(f"dreg_gps_speed                : {um7.dreg_gps_speed}")
    print(f"dreg_gps_time                 : {um7.dreg_gps_time}")
    print(f"dreg_gps_sat_1_2              : {um7.dreg_gps_sat_1_2}")
    print(f"dreg_gps_sat_3_4              : {um7.dreg_gps_sat_3_4}")
    print(f"dreg_gps_sat_5_6              : {um7.dreg_gps_sat_5_6}")
    print(f"dreg_gps_sat_7_8              : {um7.dreg_gps_sat_7_8}")
    print(f"dreg_gps_sat_9_10             : {um7.dreg_gps_sat_9_10}")
    print(f"dreg_gps_sat_11_12            : {um7.dreg_gps_sat_11_12}")
    print(f"dreg_gyro_bias_x              : {um7.dreg_gyro_bias_x}")
    print(f"dreg_gyro_bias_y              : {um7.dreg_gyro_bias_y}")
    print(f"dreg_gyro_bias_z              : {um7.dreg_gyro_bias_z}")

