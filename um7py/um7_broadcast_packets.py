#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 23 May 2020


from dataclasses import dataclass


@dataclass
class UM7AllRawPacket:
    gyro_raw_x: int
    gyro_raw_y: int
    gyro_raw_z: int
    gyro_raw_time: float
    accel_raw_x: int
    accel_raw_y: int
    accel_raw_z: int
    accel_raw_time: float
    mag_raw_x: int
    mag_raw_y: int
    mag_raw_z: int
    mag_raw_time: float
    temperature: float
    temperature_time: float

    def __repr__(self):
        return f"RawPacket("\
               f"gyro=[{self.gyro_raw_x:>+5d}, {self.gyro_raw_y:>+5d}, {self.gyro_raw_z:>+5d}], "\
               f"gyro_t={self.gyro_raw_time:>6.3f}; " \
               f"accel=[{self.accel_raw_x:>+5d}, {self.accel_raw_y:>+5d}, {self.accel_raw_z:>+5d}], " \
               f"accel_t={self.accel_raw_time:>6.3f}; " \
               f"mag=[{self.mag_raw_x:>+8d}, {self.mag_raw_y:>+8d}, {self.mag_raw_z:>+8d}], " \
               f"mag_t={self.mag_raw_time:>6.3f}; " \
               f"T={self.temperature:>+3.2f}, " \
               f"T_t={self.temperature_time:>6.3f})"


@dataclass
class UM7AllProcPacket:
    gyro_proc_x: float
    gyro_proc_y: float
    gyro_proc_z: float
    gyro_proc_time: float
    accel_proc_x: float
    accel_proc_y: float
    accel_proc_z: float
    accel_proc_time: float
    mag_proc_x: float
    mag_proc_y: float
    mag_proc_z: float
    mag_proc_time: float

    def __repr__(self):
        return f"ProcPacket("\
               f"gyro=[{self.gyro_proc_x:>+8.3f}, {self.gyro_proc_y:>+8.3f}, {self.gyro_proc_z:>+8.3f}], "\
               f"gyro_t={self.gyro_proc_time:>6.3f}; " \
               f"accel=[{self.accel_proc_x:>+8.3f}, {self.accel_proc_y:>+8.3f}, {self.accel_proc_z:>+8.3f}], " \
               f"accel_t={self.accel_proc_time:>6.3f}; " \
               f"mag=[{self.mag_proc_x:>+8.6f}, {self.mag_proc_y:>+8.6f}, {self.mag_proc_z:>+8.6f}], " \
               f"mag_t={self.mag_proc_time:>6.3f})" \


@dataclass
class UM7EulerPacket:
    roll: float
    pitch: float
    yaw: float
    roll_rate: float
    pitch_rate: float
    yaw_rate: float
    time_stamp: float

    def __repr__(self):
        return f"EulerPacket("\
               f"roll={self.roll:>+8.3f}; pitch={self.pitch:>+8.3f}; yaw={self.yaw:>+8.3f}; "\
               f"roll_rate={self.roll_rate:>+8.3f}; pitch_rate={self.pitch_rate:>+8.3f}; yaw_rate={self.yaw_rate:>+8.3f}; " \
               f"time_stamp={self.time_stamp:>6.3f})"


@dataclass
class UM7HealthPacket:
    health: int

    def __repr__(self):
        return f"HealthPacket("\
               f"raw_value=0x{self.health:04X}   ->   " \
               f"SATS_USED={(self.health >> 26) & 0x3F}, " \
               f"HDOP={(self.health >> 16) & 0x7F}, " \
               f"SATS_IN_VIEW={(self.health >> 10) & 0x3F}, " \
               f"OVF={bool((self.health >> 8) & 0x01)}, " \
               f"MG_N={bool((self.health >> 5) & 0x01)}, " \
               f"ACC_N={bool((self.health >> 4) & 0x01)}, " \
               f"ACCEL={bool((self.health >> 3) & 0x01)}, "\
               f"GYRO={bool((self.health >> 2) & 0x01)}, " \
               f"MAG={bool((self.health >> 1) & 0x01)}, " \
               f"GPS={bool((self.health >> 0) & 0x01)})"


@dataclass
class UM7RawAccelPacket:
    accel_raw_x: int
    accel_raw_y: int
    accel_raw_z: int
    accel_raw_time: float


@dataclass
class UM7RawGyroPacket:
    gyro_raw_x: int
    gyro_raw_y: int
    gyro_raw_z: int
    gyro_raw_time: float


@dataclass
class UM7RawMagPacket:
    mag_raw_x: int
    mag_raw_y: int
    mag_raw_z: int
    mag_raw_time: float


@dataclass
class UM7TemperaturePacket:
    temperature: float
    temperature_time: float


@dataclass
class UM7ProcAccelPacket:
    accel_proc_x: float
    accel_proc_y: float
    accel_proc_z: float
    accel_proc_time: float


@dataclass
class UM7ProcGyroPacket:
    gyro_proc_x: float
    gyro_proc_y: float
    gyro_proc_z: float
    gyro_proc_time: float


@dataclass
class UM7ProcMagPacket:
    mag_proc_x: float
    mag_proc_y: float
    mag_proc_z: float
    mag_proc_time: float


@dataclass
class UM7QuaternionPacket:
    q_w: float
    q_x: float
    q_y: float
    q_z: float
    q_time: float


@dataclass
class UM7EulerPosePacket:
    roll: float
    pitch: float
    yaw: float
    roll_rate: float
    pitch_rate: float
    yaw_rate: float
    euler_time: float
    position_north: float
    position_east: float
    position_up: float
    position_time: float


@dataclass
class UM7PosePacket:
    position_north: float
    position_east: float
    position_up: float
    position_time: float


@dataclass
class UM7VelocityPacket:
    velocity_north: float
    velocity_east: float
    velocity_up: float
    velocity_time: float


@dataclass
class UM7GyroBiasPacket:
    gyro_1_bias_x: float
    gyro_1_bias_y: float
    gyro_1_bias_z: float


if __name__ == '__main__':
    pass

