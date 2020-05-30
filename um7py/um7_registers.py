#!/usr/bin/env python

# Author: Dr. Konstantin Selyunin
# License: MIT
# Created: 2020.05.29

import os.path
import struct

from abc import abstractmethod, ABC
from typing import Union

from um7py.rsl_xml_svd.rsl_svd_parser import RslSvdParser


class UM7Registers(ABC):

    def __init__(self, **kwargs):
        self.svd_parser = RslSvdParser(svd_file=UM7Registers.find_svd('um7.svd'))

    @staticmethod
    def find_svd(svd_file_name: str):
        parent_dir = os.path.join(os.path.dirname(__file__), os.pardir)
        for root, dirs, files in os.walk(parent_dir):
            if svd_file_name in files:
                return os.path.join(root, svd_file_name)

    @abstractmethod
    def connect(self, *args, **kwargs):
        pass

    @abstractmethod
    def read_register(self, reg_addr: int, **kw) -> bytes:
        pass

    @abstractmethod
    def write_register(self, reg_addr: int, reg_value: Union[int, bytes, float], **kw):
        pass


    @property
    def creg_com_settings(self):
        """
        The CREG_COM_SETTINGS register is used to set the boards serial port baud rate and to enable (disable) the
        automatic transmission of sensor data and estimated states (telemetry).
        Payload structure:
        [31:28] : BAUD_RATE -- Sets the baud rate of the boards main serial port:
        [27:24] : GPS_BAUD -- Sets the baud rate of the UM7 auxiliary serial port:
        [8]     : GPS -- If set, this bit causes GPS data to be transmitted automatically whenever new GPS data is received. GPS data is stored in registers 125 to 130. These registers will be transmitted in a batch packet of length 6 starting at address 125.
        [4]     : SAT -- If set, this bit causes satellite details to be transmitted whenever they are provided by the GPS. Satellite information is stored in registers 131 to 136. These registers will be transmitted in a batch packet of length 6 beginning at address 131.
        :return:  BAUD_RATE as bitField; GPS_BAUD as bitField; GPS as bitField; SAT as bitField; 
        """
        addr = 0x00
        ok, payload = self.read_register(addr)
        if ok:
            payload_uint32, = struct.unpack('>I', payload[0:4])
            reg = self.svd_parser.find_register_by(name='CREG_COM_SETTINGS')
            # find value for BAUD_RATE bit field
            baud_rate_val = (payload_uint32 >> 28) & 0x000F
            baud_rate_enum = reg.find_field_by(name='BAUD_RATE').find_enum_entry_by(value=baud_rate_val)
            # find value for GPS_BAUD bit field
            gps_baud_val = (payload_uint32 >> 24) & 0x000F
            gps_baud_enum = reg.find_field_by(name='GPS_BAUD').find_enum_entry_by(value=gps_baud_val)
            # find value for GPS bit field
            gps_val = (payload_uint32 >> 8) & 0x0001
            gps_enum = reg.find_field_by(name='GPS').find_enum_entry_by(value=gps_val)
            # find value for SAT bit field
            sat_val = (payload_uint32 >> 4) & 0x0001
            sat_enum = reg.find_field_by(name='SAT').find_enum_entry_by(value=sat_val)

            return baud_rate_enum, gps_baud_enum, gps_enum, sat_enum
        else:
            return None

    @creg_com_settings.setter
    def creg_com_settings(self, new_value):
        addr = 0x00
        self.write_register(addr, new_value)

    @property
    def creg_com_rates1(self):
        """
        The CREG_COM_RATES1 register sets desired telemetry transmission rates in Hz for raw accelerometer, gyro, and
        magnetometer data. If the specified rate is 0, then no data is transmitted.
        Payload structure:
        [31:24] : RAW_ACCEL_RATE -- Specifies the desired raw accelerometer data broadcast rate in Hz. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [23:16] : RAW_GYRO_RATE -- Specifies the desired raw gyro data broadcast rate in Hz. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [15:8]  : RAW_MAG_RATE -- Specifies the desired raw magnetometer data broadcast rate in Hz. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  RAW_ACCEL_RATE as uint8_t; RAW_GYRO_RATE as uint8_t; RAW_MAG_RATE as uint8_t; 
        """
        addr = 0x01
        ok, payload = self.read_register(addr)
        if ok:
            raw_accel_rate, raw_gyro_rate, raw_mag_rate = struct.unpack('>BBBx', payload[0:4])
            return raw_accel_rate, raw_gyro_rate, raw_mag_rate
        else:
            return None

    @creg_com_rates1.setter
    def creg_com_rates1(self, new_value):
        addr = 0x01
        self.write_register(addr, new_value)

    @property
    def creg_com_rates2(self):
        """
        The CREG_COM_RATES2 register sets desired telemetry transmission rates for all raw data and temperature. If
        the specified rate is 0, then no data is transmitted.
        Payload structure:
        [31:24] : TEMP_RATE -- Specifies the desired broadcast rate for temperature data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [7:0]   : ALL_RAW_RATE -- Specifies the desired broadcast rate for all raw sensor data. If set, this overrides the broadcast rate setting for individual raw data broadcast rates. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  TEMP_RATE as uint8_t; ALL_RAW_RATE as uint8_t; 
        """
        addr = 0x02
        ok, payload = self.read_register(addr)
        if ok:
            temp_rate, all_raw_rate = struct.unpack('>BxxB', payload[0:4])
            return temp_rate, all_raw_rate
        else:
            return None

    @creg_com_rates2.setter
    def creg_com_rates2(self, new_value):
        addr = 0x02
        self.write_register(addr, new_value)

    @property
    def creg_com_rates3(self):
        """
        The CREG_COM_RATES3 register sets desired telemetry transmission rates for processed sensor data. If the
        specified rate is 0, then no data is transmitted.
        Payload structure:
        [31:24] : PROC_ACCEL_RATE -- Specifies the desired broadcast rate for processed accelerometer data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [23:16] : PROC_GYRO_RATE -- Specifies the desired broadcast rate for processed rate gyro data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [15:8]  : PROC_MAG_RATE -- Specifies the desired broadcast rate for processed magnetometer data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  PROC_ACCEL_RATE as uint8_t; PROC_GYRO_RATE as uint8_t; PROC_MAG_RATE as uint8_t; 
        """
        addr = 0x03
        ok, payload = self.read_register(addr)
        if ok:
            proc_accel_rate, proc_gyro_rate, proc_mag_rate = struct.unpack('>BBBx', payload[0:4])
            return proc_accel_rate, proc_gyro_rate, proc_mag_rate
        else:
            return None

    @creg_com_rates3.setter
    def creg_com_rates3(self, new_value):
        addr = 0x03
        self.write_register(addr, new_value)

    @property
    def creg_com_rates4(self):
        """
        The CREG_COM_RATES4 register defines the desired telemetry transmission rates for all processed data. If the
        specified rate is 0, then no data is transmitted.
        Payload structure:
        [7:0]   : ALL_PROC_RATE -- Specifies the desired broadcast rate for raw all processed data. If set, this overrides the broadcast rate setting for individual processed data broadcast rates. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  ALL_PROC_RATE as uint8_t; 
        """
        addr = 0x04
        ok, payload = self.read_register(addr)
        if ok:
            all_proc_rate = struct.unpack('>xxxB', payload[0:4])
            return all_proc_rate
        else:
            return None

    @creg_com_rates4.setter
    def creg_com_rates4(self, new_value):
        addr = 0x04
        self.write_register(addr, new_value)

    @property
    def creg_com_rates5(self):
        """
        The CREG_COM_RATES5 register sets desired telemetry transmission rates for quaternions, Euler Angles,
        position, and velocity estimates. If the specified rate is 0, then no data is transmitted.
        Payload structure:
        [31:24] : QUAT_RATE -- Specifies the desired broadcast rate for quaternion data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [23:16] : EULER_RATE -- Specifies the desired broadcast rate for Euler Angle data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [15:8]  : POSITION_RATE -- Specifies the desired broadcast rate position. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [7:0]   : VELOCITY_RATE -- Specifies the desired broadcast rate for velocity. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  QUAT_RATE as uint8_t; EULER_RATE as uint8_t; POSITION_RATE as uint8_t; VELOCITY_RATE as uint8_t; 
        """
        addr = 0x05
        ok, payload = self.read_register(addr)
        if ok:
            quat_rate, euler_rate, position_rate, velocity_rate = struct.unpack('>BBBB', payload[0:4])
            return quat_rate, euler_rate, position_rate, velocity_rate
        else:
            return None

    @creg_com_rates5.setter
    def creg_com_rates5(self, new_value):
        addr = 0x05
        self.write_register(addr, new_value)

    @property
    def creg_com_rates6(self):
        """
        The CREG_COM_RATES6 register sets desired telemetry transmission rates for pose (Euler/position packet),
        health, and gyro bias estimates for the gyro 1 and gyro 2. If the specified rate is 0, then no data is
        transmitted.
        Payload structure:
        [31:24] : POSE_RATE -- Specifies the desired broadcast rate for pose (Euler Angle and position) data. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        [19:16] : HEALTH_RATE -- Specifies the desired broadcast rate for the sensor health packet.
        [15:8]  : GYRO_BIAS_RATE -- Specifies the desired broadcast rate for gyro bias estimates. The data is stored as an unsigned 8-bit integer, yielding a maximum rate of 255 Hz.
        :return:  POSE_RATE as uint8_t; HEALTH_RATE as bitField; GYRO_BIAS_RATE as uint8_t; 
        """
        addr = 0x06
        ok, payload = self.read_register(addr)
        if ok:
            pose_rate, gyro_bias_rate = struct.unpack('>BxBx', payload[0:4])
            payload_uint32, = struct.unpack('>I', payload[0:4])
            reg = self.svd_parser.find_register_by(name='CREG_COM_RATES6')
            # find value for HEALTH_RATE bit field
            health_rate_val = (payload_uint32 >> 16) & 0x000F
            health_rate_enum = reg.find_field_by(name='HEALTH_RATE').find_enum_entry_by(value=health_rate_val)

            return pose_rate, gyro_bias_rate, health_rate_enum
        else:
            return None

    @creg_com_rates6.setter
    def creg_com_rates6(self, new_value):
        addr = 0x06
        self.write_register(addr, new_value)

    @property
    def creg_com_rates7(self):
        """
        The CREG_COM_RATES7 register sets desired telemetry transmission rates in Hz for NMEA packets.
        Payload structure:
        [31:28] : NMEA_HEALTH_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style health packet.
        [27:24] : NMEA_POSE_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style pose (Euler Angle/position) packet.
        [23:20] : NMEA_ATTITUDE_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style attitude packet.
        [19:16] : NMEA_SENSOR_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style sensor data packet.
        [15:12] : NMEA_RATES_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style rate data packet.
        [11:8]  : NMEA_GPS_POSE_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style GPS pose packet.
        [7:4]   : NMEA_QUAT_RATE -- Specifies the desired broadcast rate for Redshift Labs Pty Ltd NMEA-style quaternion packet.
        :return:  NMEA_HEALTH_RATE as bitField; NMEA_POSE_RATE as bitField; NMEA_ATTITUDE_RATE as bitField; NMEA_SENSOR_RATE as bitField; NMEA_RATES_RATE as bitField; NMEA_GPS_POSE_RATE as bitField; NMEA_QUAT_RATE as bitField; 
        """
        addr = 0x07
        ok, payload = self.read_register(addr)
        if ok:
            payload_uint32, = struct.unpack('>I', payload[0:4])
            reg = self.svd_parser.find_register_by(name='CREG_COM_RATES7')
            # find value for NMEA_HEALTH_RATE bit field
            nmea_health_rate_val = (payload_uint32 >> 28) & 0x000F
            nmea_health_rate_enum = reg.find_field_by(name='NMEA_HEALTH_RATE').find_enum_entry_by(value=nmea_health_rate_val)
            # find value for NMEA_POSE_RATE bit field
            nmea_pose_rate_val = (payload_uint32 >> 24) & 0x000F
            nmea_pose_rate_enum = reg.find_field_by(name='NMEA_POSE_RATE').find_enum_entry_by(value=nmea_pose_rate_val)
            # find value for NMEA_ATTITUDE_RATE bit field
            nmea_attitude_rate_val = (payload_uint32 >> 20) & 0x000F
            nmea_attitude_rate_enum = reg.find_field_by(name='NMEA_ATTITUDE_RATE').find_enum_entry_by(value=nmea_attitude_rate_val)
            # find value for NMEA_SENSOR_RATE bit field
            nmea_sensor_rate_val = (payload_uint32 >> 16) & 0x000F
            nmea_sensor_rate_enum = reg.find_field_by(name='NMEA_SENSOR_RATE').find_enum_entry_by(value=nmea_sensor_rate_val)
            # find value for NMEA_RATES_RATE bit field
            nmea_rates_rate_val = (payload_uint32 >> 12) & 0x000F
            nmea_rates_rate_enum = reg.find_field_by(name='NMEA_RATES_RATE').find_enum_entry_by(value=nmea_rates_rate_val)
            # find value for NMEA_GPS_POSE_RATE bit field
            nmea_gps_pose_rate_val = (payload_uint32 >> 8) & 0x000F
            nmea_gps_pose_rate_enum = reg.find_field_by(name='NMEA_GPS_POSE_RATE').find_enum_entry_by(value=nmea_gps_pose_rate_val)
            # find value for NMEA_QUAT_RATE bit field
            nmea_quat_rate_val = (payload_uint32 >> 4) & 0x000F
            nmea_quat_rate_enum = reg.find_field_by(name='NMEA_QUAT_RATE').find_enum_entry_by(value=nmea_quat_rate_val)

            return nmea_health_rate_enum, nmea_pose_rate_enum, nmea_attitude_rate_enum, nmea_sensor_rate_enum, nmea_rates_rate_enum, nmea_gps_pose_rate_enum, nmea_quat_rate_enum
        else:
            return None

    @creg_com_rates7.setter
    def creg_com_rates7(self, new_value):
        addr = 0x07
        self.write_register(addr, new_value)

    @property
    def creg_misc_settings(self):
        """
        This register contains miscellaneous filter and sensor control options.
        Payload structure:
        [8]     : PPS -- If set, this bit causes the TX2 pin on the IO Expansion header to be used as the PPS input from an external GPS module. PPS pulses will then be used to synchronize the system clock to UTC time of day.
        [2]     : ZG -- If set, this bit causes the device to attempt to measure the rate gyro bias on startup. The sensor must be stationary on startup for this feature to work properly.
        [1]     : Q -- If this bit is set, the sensor will run in quaternion mode instead of Euler Angle mode.
        [0]     : MAG -- If set, the magnetometer will be used in state updates.
        :return:  PPS as bitField; ZG as bitField; Q as bitField; MAG as bitField; 
        """
        addr = 0x08
        ok, payload = self.read_register(addr)
        if ok:
            payload_uint32, = struct.unpack('>I', payload[0:4])
            reg = self.svd_parser.find_register_by(name='CREG_MISC_SETTINGS')
            # find value for PPS bit field
            pps_val = (payload_uint32 >> 8) & 0x0001
            pps_enum = reg.find_field_by(name='PPS').find_enum_entry_by(value=pps_val)
            # find value for ZG bit field
            zg_val = (payload_uint32 >> 2) & 0x0001
            zg_enum = reg.find_field_by(name='ZG').find_enum_entry_by(value=zg_val)
            # find value for Q bit field
            q_val = (payload_uint32 >> 1) & 0x0001
            q_enum = reg.find_field_by(name='Q').find_enum_entry_by(value=q_val)
            # find value for MAG bit field
            mag_val = (payload_uint32 >> 0) & 0x0001
            mag_enum = reg.find_field_by(name='MAG').find_enum_entry_by(value=mag_val)

            return pps_enum, zg_enum, q_enum, mag_enum
        else:
            return None

    @creg_misc_settings.setter
    def creg_misc_settings(self, new_value):
        addr = 0x08
        self.write_register(addr, new_value)

    @property
    def creg_home_north(self):
        """
        This register sets the north home latitude in degrees, used to convert GPS coordinates to position in meters
        from home.
        Payload structure:
        [31:0]  : SET_HOME_NORTH -- North Position (32-bit IEEE Floating Point Value)
        :return:  SET_HOME_NORTH as float; 
        """
        addr = 0x09
        ok, payload = self.read_register(addr)
        if ok:
            set_home_north = struct.unpack('>f', payload[0:4])
            return set_home_north
        else:
            return None

    @creg_home_north.setter
    def creg_home_north(self, new_value):
        addr = 0x09
        self.write_register(addr, new_value)

    @property
    def creg_home_east(self):
        """
        This register sets the east home longitude in degrees, used to convert GPS coordinates to position in meters
        from home.
        Payload structure:
        [31:0]  : SET_HOME_EAST -- East Position (32-bit IEEE Floating Point Value)
        :return:  SET_HOME_EAST as float; 
        """
        addr = 0x0A
        ok, payload = self.read_register(addr)
        if ok:
            set_home_east = struct.unpack('>f', payload[0:4])
            return set_home_east
        else:
            return None

    @creg_home_east.setter
    def creg_home_east(self, new_value):
        addr = 0x0A
        self.write_register(addr, new_value)

    @property
    def creg_home_up(self):
        """
        This register sets the home altitude in meters. Used to convert GPS coordinates to position in meters from
        home.
        Payload structure:
        [31:0]  : SET_HOME_UP -- Altitude Position (32-bit IEEE Floating Point Value)
        :return:  SET_HOME_UP as float; 
        """
        addr = 0x0B
        ok, payload = self.read_register(addr)
        if ok:
            set_home_up = struct.unpack('>f', payload[0:4])
            return set_home_up
        else:
            return None

    @creg_home_up.setter
    def creg_home_up(self, new_value):
        addr = 0x0B
        self.write_register(addr, new_value)

    @property
    def creg_gyro_trim_x(self):
        """
        This register sets the x-axis rate gyro trim, which is used to add additional bias compensation for the rate
        gyros during calls to the ZERO_GYRO_BIAS command.
        Payload structure:
        [31:0]  : GYRO_TRIM_X -- 32-bit IEEE Floating Point Value
        :return:  GYRO_TRIM_X as float; 
        """
        addr = 0x0C
        ok, payload = self.read_register(addr)
        if ok:
            gyro_trim_x = struct.unpack('>f', payload[0:4])
            return gyro_trim_x
        else:
            return None

    @creg_gyro_trim_x.setter
    def creg_gyro_trim_x(self, new_value):
        addr = 0x0C
        self.write_register(addr, new_value)

    @property
    def creg_gyro_trim_y(self):
        """
        This register sets the y-axis rate gyro trim, which is used to add additional bias compensation for the rate
        gyros during calls to the ZERO_GYRO_BIAS command.
        Payload structure:
        [31:0]  : GYRO_TRIM_Y -- 32-bit IEEE Floating Point Value
        :return:  GYRO_TRIM_Y as float; 
        """
        addr = 0x0D
        ok, payload = self.read_register(addr)
        if ok:
            gyro_trim_y = struct.unpack('>f', payload[0:4])
            return gyro_trim_y
        else:
            return None

    @creg_gyro_trim_y.setter
    def creg_gyro_trim_y(self, new_value):
        addr = 0x0D
        self.write_register(addr, new_value)

    @property
    def creg_gyro_trim_z(self):
        """
        This register sets the z-axis rate gyro trim, which is used to add additional bias compensation for the rate
        gyros during calls to the ZERO_GYRO_BIAS command.
        Payload structure:
        [31:0]  : GYRO_TRIM_Z -- 32-bit IEEE Floating Point Value
        :return:  GYRO_TRIM_Z as float; 
        """
        addr = 0x0E
        ok, payload = self.read_register(addr)
        if ok:
            gyro_trim_z = struct.unpack('>f', payload[0:4])
            return gyro_trim_z
        else:
            return None

    @creg_gyro_trim_z.setter
    def creg_gyro_trim_z(self, new_value):
        addr = 0x0E
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal1_1(self):
        """
        Row 1, Column 1 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL1_1 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL1_1 as float; 
        """
        addr = 0x0F
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal1_1 = struct.unpack('>f', payload[0:4])
            return mag_cal1_1
        else:
            return None

    @creg_mag_cal1_1.setter
    def creg_mag_cal1_1(self, new_value):
        addr = 0x0F
        self.write_register(addr, new_value)

    @property
    def creg_mag_1_cal1_2(self):
        """
        Row 1, Column 2 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL1_2 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL1_2 as float; 
        """
        addr = 0x10
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal1_2 = struct.unpack('>f', payload[0:4])
            return mag_cal1_2
        else:
            return None

    @creg_mag_1_cal1_2.setter
    def creg_mag_1_cal1_2(self, new_value):
        addr = 0x10
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal1_3(self):
        """
        Row 1, Column 3 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL1_3 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL1_3 as float; 
        """
        addr = 0x11
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal1_3 = struct.unpack('>f', payload[0:4])
            return mag_cal1_3
        else:
            return None

    @creg_mag_cal1_3.setter
    def creg_mag_cal1_3(self, new_value):
        addr = 0x11
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal2_1(self):
        """
        Row 2, Column 1 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL2_1 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL2_1 as float; 
        """
        addr = 0x12
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal2_1 = struct.unpack('>f', payload[0:4])
            return mag_cal2_1
        else:
            return None

    @creg_mag_cal2_1.setter
    def creg_mag_cal2_1(self, new_value):
        addr = 0x12
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal2_2(self):
        """
        Row 2, Column 2 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL2_2 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL2_2 as float; 
        """
        addr = 0x13
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal2_2 = struct.unpack('>f', payload[0:4])
            return mag_cal2_2
        else:
            return None

    @creg_mag_cal2_2.setter
    def creg_mag_cal2_2(self, new_value):
        addr = 0x13
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal2_3(self):
        """
        Row 2, Column 3 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL2_3 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL2_3 as float; 
        """
        addr = 0x14
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal2_3 = struct.unpack('>f', payload[0:4])
            return mag_cal2_3
        else:
            return None

    @creg_mag_cal2_3.setter
    def creg_mag_cal2_3(self, new_value):
        addr = 0x14
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal3_1(self):
        """
        Row 3, Column 1 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL3_1 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL3_1 as float; 
        """
        addr = 0x15
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal3_1 = struct.unpack('>f', payload[0:4])
            return mag_cal3_1
        else:
            return None

    @creg_mag_cal3_1.setter
    def creg_mag_cal3_1(self, new_value):
        addr = 0x15
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal3_2(self):
        """
        Row 3, Column 2 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL3_2 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL3_2 as float; 
        """
        addr = 0x16
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal3_2 = struct.unpack('>f', payload[0:4])
            return mag_cal3_2
        else:
            return None

    @creg_mag_cal3_2.setter
    def creg_mag_cal3_2(self, new_value):
        addr = 0x16
        self.write_register(addr, new_value)

    @property
    def creg_mag_cal3_3(self):
        """
        Row 3, Column 3 of magnetometer calibration matrix.
        Payload structure:
        [31:0]  : MAG_CAL3_3 -- 32-bit IEEE Floating Point Value
        :return:  MAG_CAL3_3 as float; 
        """
        addr = 0x64
        ok, payload = self.read_register(addr)
        if ok:
            mag_cal3_3 = struct.unpack('>f', payload[0:4])
            return mag_cal3_3
        else:
            return None

    @creg_mag_cal3_3.setter
    def creg_mag_cal3_3(self, new_value):
        addr = 0x64
        self.write_register(addr, new_value)

    @property
    def creg_mag_bias_x(self):
        """
        This register stores a bias term for the magnetometer x-axis for hard-iron calibration. This term can be
        computed by performing magnetometer calibration with the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : MAG_BIAS_X -- 32-bit IEEE Floating Point Value
        :return:  MAG_BIAS_X as float; 
        """
        addr = 0x18
        ok, payload = self.read_register(addr)
        if ok:
            mag_bias_x = struct.unpack('>f', payload[0:4])
            return mag_bias_x
        else:
            return None

    @creg_mag_bias_x.setter
    def creg_mag_bias_x(self, new_value):
        addr = 0x18
        self.write_register(addr, new_value)

    @property
    def creg_mag_1_bias_y(self):
        """
        This register stores a bias term for the magnetometer y-axis for hard-iron calibration. This term can be
        computed by performing magnetometer calibration with the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : MAG_BIAS_Y -- 32-bit IEEE Floating Point Value
        :return:  MAG_BIAS_Y as float; 
        """
        addr = 0x19
        ok, payload = self.read_register(addr)
        if ok:
            mag_bias_y = struct.unpack('>f', payload[0:4])
            return mag_bias_y
        else:
            return None

    @creg_mag_1_bias_y.setter
    def creg_mag_1_bias_y(self, new_value):
        addr = 0x19
        self.write_register(addr, new_value)

    @property
    def creg_mag_bias_z(self):
        """
        This register stores a bias term for the magnetometer z-axis for hard-iron calibration. This term can be
        computed by performing magnetometer calibration with the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : MAG_BIAS_Z -- 32-bit IEEE Floating Point Value
        :return:  MAG_BIAS_Z as float; 
        """
        addr = 0x1A
        ok, payload = self.read_register(addr)
        if ok:
            mag_bias_z = struct.unpack('>f', payload[0:4])
            return mag_bias_z
        else:
            return None

    @creg_mag_bias_z.setter
    def creg_mag_bias_z(self, new_value):
        addr = 0x1A
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal1_1(self):
        """
        Row 1, Column 1 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL1_1 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL1_1 as float; 
        """
        addr = 0x1B
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal1_1 = struct.unpack('>f', payload[0:4])
            return accel_cal1_1
        else:
            return None

    @creg_accel_cal1_1.setter
    def creg_accel_cal1_1(self, new_value):
        addr = 0x1B
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal1_2(self):
        """
        Row 1, Column 2 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL1_2 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL1_2 as float; 
        """
        addr = 0x1C
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal1_2 = struct.unpack('>f', payload[0:4])
            return accel_cal1_2
        else:
            return None

    @creg_accel_cal1_2.setter
    def creg_accel_cal1_2(self, new_value):
        addr = 0x1C
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal1_3(self):
        """
        Row 1, Column 3 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL1_3 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL1_3 as float; 
        """
        addr = 0x1D
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal1_3 = struct.unpack('>f', payload[0:4])
            return accel_cal1_3
        else:
            return None

    @creg_accel_cal1_3.setter
    def creg_accel_cal1_3(self, new_value):
        addr = 0x1D
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal2_1(self):
        """
        Row 2, Column 1 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL2_1 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL2_1 as float; 
        """
        addr = 0x1E
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal2_1 = struct.unpack('>f', payload[0:4])
            return accel_cal2_1
        else:
            return None

    @creg_accel_cal2_1.setter
    def creg_accel_cal2_1(self, new_value):
        addr = 0x1E
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal2_2(self):
        """
        Row 2, Column 2 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL2_2 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL2_2 as float; 
        """
        addr = 0x1F
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal2_2 = struct.unpack('>f', payload[0:4])
            return accel_cal2_2
        else:
            return None

    @creg_accel_cal2_2.setter
    def creg_accel_cal2_2(self, new_value):
        addr = 0x1F
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal2_3(self):
        """
        Row 2, Column 3 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL2_3 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL2_3 as float; 
        """
        addr = 0x20
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal2_3 = struct.unpack('>f', payload[0:4])
            return accel_cal2_3
        else:
            return None

    @creg_accel_cal2_3.setter
    def creg_accel_cal2_3(self, new_value):
        addr = 0x20
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal3_1(self):
        """
        Row 3, Column 1 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL3_1 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL3_1 as float; 
        """
        addr = 0x21
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal3_1 = struct.unpack('>f', payload[0:4])
            return accel_cal3_1
        else:
            return None

    @creg_accel_cal3_1.setter
    def creg_accel_cal3_1(self, new_value):
        addr = 0x21
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal3_2(self):
        """
        Row 3, Column 2 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL3_2 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL3_2 as float; 
        """
        addr = 0x22
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal3_2 = struct.unpack('>f', payload[0:4])
            return accel_cal3_2
        else:
            return None

    @creg_accel_cal3_2.setter
    def creg_accel_cal3_2(self, new_value):
        addr = 0x22
        self.write_register(addr, new_value)

    @property
    def creg_accel_cal3_3(self):
        """
        Row 3, Column 3 of accelerometer calibration matrix.
        Payload structure:
        [31:0]  : ACCEL_CAL3_3 -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_CAL3_3 as float; 
        """
        addr = 0x23
        ok, payload = self.read_register(addr)
        if ok:
            accel_cal3_3 = struct.unpack('>f', payload[0:4])
            return accel_cal3_3
        else:
            return None

    @creg_accel_cal3_3.setter
    def creg_accel_cal3_3(self, new_value):
        addr = 0x23
        self.write_register(addr, new_value)

    @property
    def creg_accel_bias_x(self):
        """
        This register stores a bias term for the accelerometer x-axis for bias calibration. This term can be computed
        by performing calibrate accelerometers command within the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : ACCEL_BIAS_X -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_BIAS_X as float; 
        """
        addr = 0x24
        ok, payload = self.read_register(addr)
        if ok:
            accel_bias_x = struct.unpack('>f', payload[0:4])
            return accel_bias_x
        else:
            return None

    @creg_accel_bias_x.setter
    def creg_accel_bias_x(self, new_value):
        addr = 0x24
        self.write_register(addr, new_value)

    @property
    def creg_accel_bias_y(self):
        """
        This register stores a bias term for the accelerometer y-axis for bias calibration. This term can be computed
        by performing calibrate accelerometers command within the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : ACCEL_BIAS_Y -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_BIAS_Y as float; 
        """
        addr = 0x25
        ok, payload = self.read_register(addr)
        if ok:
            accel_bias_y = struct.unpack('>f', payload[0:4])
            return accel_bias_y
        else:
            return None

    @creg_accel_bias_y.setter
    def creg_accel_bias_y(self, new_value):
        addr = 0x25
        self.write_register(addr, new_value)

    @property
    def creg_accel_bias_z(self):
        """
        This register stores a bias term for the accelerometer z-axis for bias calibration. This term can be computed
        by performing calibrate accelerometers command within the Redshift labs Serial Interface.
        Payload structure:
        [31:0]  : ACCEL_BIAS_Z -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_BIAS_Z as float; 
        """
        addr = 0x26
        ok, payload = self.read_register(addr)
        if ok:
            accel_bias_z = struct.unpack('>f', payload[0:4])
            return accel_bias_z
        else:
            return None

    @creg_accel_bias_z.setter
    def creg_accel_bias_z(self, new_value):
        addr = 0x26
        self.write_register(addr, new_value)

    @property
    def dreg_health(self):
        """
        The health register reports the current status of the GPS module and the other sensors on the board.
        Monitoring the health register is the easiest way to monitor the quality of the GPS lock and to watch for
        other problems that could affect the behavior of the board.
        Payload structure:
        [31:26] : SATS_USED -- Reports the number of satellites used in the position solution.
        [25:16] : HDOP -- Reports the horizontal dilution of precision (HDOP) reported by the GPS. The actual HDOP value is equal to the contents of the HDOP bits divided by 10.
        [15:10] : SATS_IN_VIEW -- Reports the number of satellites in view.
        [8]     : OVF -- Overflow bit. This bit is set if the UM7 is attempting to transmit data over the serial port faster than is allowed given the baud-rate. If this bit is set, reduce broadcast rates in the COM_RATES registers.
        [5]     : MG_N -- This bit is set if the sensor detects that the norm of the magnetometer measurement is too far away from 1.0 to be trusted. Usually indicates bad calibration, local field distortions, or both.
        [4]     : ACC_N -- This bit is set if the sensor detects that the norm of the accelerometer measurement is too far away from 1G to be used (i.e. during aggressive acceleration or high vibration).
        [3]     : ACCEL -- This bit will be set if the accelerometer fails to initialize on startup.
        [2]     : GYRO -- This bit will be set if the rate gyro fails to initialize on startup.
        [1]     : MAG -- This bit will be set if the magnetometer fails to initialize on startup.
        [0]     : GPS -- This bit is set if the GPS fails to send a packet for more than two seconds. If a GPS packet is ever received, this bit is cleared.
        :return:  SATS_USED as bitField; HDOP as bitField; SATS_IN_VIEW as bitField; OVF as bitField; MG_N as bitField; ACC_N as bitField; ACCEL as bitField; GYRO as bitField; MAG as bitField; GPS as bitField; 
        """
        addr = 0x55
        ok, payload = self.read_register(addr)
        if ok:
            payload_uint32, = struct.unpack('>I', payload[0:4])
            reg = self.svd_parser.find_register_by(name='DREG_HEALTH')
            # find value for SATS_USED bit field
            sats_used_val = (payload_uint32 >> 26) & 0x003F
            # find value for HDOP bit field
            hdop_val = (payload_uint32 >> 16) & 0x03FF
            # find value for SATS_IN_VIEW bit field
            sats_in_view_val = (payload_uint32 >> 10) & 0x003F
            # find value for OVF bit field
            ovf_val = (payload_uint32 >> 8) & 0x0001
            ovf_enum = reg.find_field_by(name='OVF').find_enum_entry_by(value=ovf_val)
            # find value for MG_N bit field
            mg_n_val = (payload_uint32 >> 5) & 0x0001
            mg_n_enum = reg.find_field_by(name='MG_N').find_enum_entry_by(value=mg_n_val)
            # find value for ACC_N bit field
            acc_n_val = (payload_uint32 >> 4) & 0x0001
            acc_n_enum = reg.find_field_by(name='ACC_N').find_enum_entry_by(value=acc_n_val)
            # find value for ACCEL bit field
            accel_val = (payload_uint32 >> 3) & 0x0001
            accel_enum = reg.find_field_by(name='ACCEL').find_enum_entry_by(value=accel_val)
            # find value for GYRO bit field
            gyro_val = (payload_uint32 >> 2) & 0x0001
            gyro_enum = reg.find_field_by(name='GYRO').find_enum_entry_by(value=gyro_val)
            # find value for MAG bit field
            mag_val = (payload_uint32 >> 1) & 0x0001
            mag_enum = reg.find_field_by(name='MAG').find_enum_entry_by(value=mag_val)
            # find value for GPS bit field
            gps_val = (payload_uint32 >> 0) & 0x0001
            gps_enum = reg.find_field_by(name='GPS').find_enum_entry_by(value=gps_val)

            return sats_used_val, hdop_val, sats_in_view_val, ovf_enum, mg_n_enum, acc_n_enum, accel_enum, gyro_enum, mag_enum, gps_enum
        else:
            return None

    @property
    def dreg_gyro_raw_xy(self):
        """
        Contains raw X and Y axis rate gyro data.
        Payload structure:
        [31:16] : GYRO_RAW_X -- Gyro X (2s complement 16-bit integer)
        [15:0]  : GYRO_RAW_Y -- Gyro Y (2s complement 16-bit integer)
        :return:  GYRO_RAW_X as int16_t; GYRO_RAW_Y as int16_t; 
        """
        addr = 0x56
        ok, payload = self.read_register(addr)
        if ok:
            gyro_raw_x, gyro_raw_y = struct.unpack('>hh', payload[0:4])
            return gyro_raw_x, gyro_raw_y
        else:
            return None

    @property
    def dreg_gyro_raw_z(self):
        """
        Contains raw Z axis rate gyro data.
        Payload structure:
        [31:16] : GYRO_RAW_Z -- Gyro Z (2s complement 16-bit integer)
        :return:  GYRO_RAW_Z as int16_t; 
        """
        addr = 0x57
        ok, payload = self.read_register(addr)
        if ok:
            gyro_raw_z = struct.unpack('>hxx', payload[0:4])
            return gyro_raw_z
        else:
            return None

    @property
    def dreg_gyro_raw_time(self):
        """
        Contains time at which the last rate gyro data was acquired.
        Payload structure:
        [31:0]  : GYRO_RAW_TIME -- 32-bit IEEE Floating Point Value
        :return:  GYRO_RAW_TIME as float; 
        """
        addr = 0x58
        ok, payload = self.read_register(addr)
        if ok:
            gyro_raw_time = struct.unpack('>f', payload[0:4])
            return gyro_raw_time
        else:
            return None

    @property
    def dreg_accel_raw_xy(self):
        """
        Contains raw X and Y axis accelerometer data.
        Payload structure:
        [31:16] : ACCEL_RAW_X -- Accel X (2s complement 16-bit integer)
        [15:0]  : ACCEL_RAW_Y -- Accel Y (2s complement 16-bit integer)
        :return:  ACCEL_RAW_X as int16_t; ACCEL_RAW_Y as int16_t; 
        """
        addr = 0x59
        ok, payload = self.read_register(addr)
        if ok:
            accel_raw_x, accel_raw_y = struct.unpack('>hh', payload[0:4])
            return accel_raw_x, accel_raw_y
        else:
            return None

    @property
    def dreg_accel_raw_z(self):
        """
        Contains raw Z axis accelerometer data.
        Payload structure:
        [31:16] : ACCEL_RAW_Z -- Accel Z (2s complement 16-bit integer)
        :return:  ACCEL_RAW_Z as int16_t; 
        """
        addr = 0x5A
        ok, payload = self.read_register(addr)
        if ok:
            accel_raw_z = struct.unpack('>hxx', payload[0:4])
            return accel_raw_z
        else:
            return None

    @property
    def dreg_accel_raw_time(self):
        """
        Contains time at which the last raw data sample for the accelerometer was acquired.
        Payload structure:
        [31:0]  : ACCEL_RAW_TIME -- 32-bit IEEE Floating Point Value
        :return:  ACCEL_RAW_TIME as float; 
        """
        addr = 0x5B
        ok, payload = self.read_register(addr)
        if ok:
            accel_raw_time = struct.unpack('>f', payload[0:4])
            return accel_raw_time
        else:
            return None

    @property
    def dreg_mag_raw_xy(self):
        """
        Contains raw X and Y axis magnetometer data.
        Payload structure:
        [31:16] : MAG_RAW_X -- Magnetometer X (2s complement 16-bit integer)
        [15:0]  : MAG_RAW_Y -- Magnetometer Y (2s complement 16-bit integer)
        :return:  MAG_RAW_X as int16_t; MAG_RAW_Y as int16_t; 
        """
        addr = 0x5C
        ok, payload = self.read_register(addr)
        if ok:
            mag_raw_x, mag_raw_y = struct.unpack('>hh', payload[0:4])
            return mag_raw_x, mag_raw_y
        else:
            return None

    @property
    def dreg_mag_raw_z(self):
        """
        Contains raw Z axis magnetometer data.
        Payload structure:
        [31:16] : MAG_RAW_Z -- Magnetometer Z (2s complement 16-bit integer)
        :return:  MAG_RAW_Z as int16_t; 
        """
        addr = 0x5D
        ok, payload = self.read_register(addr)
        if ok:
            mag_raw_z = struct.unpack('>hxx', payload[0:4])
            return mag_raw_z
        else:
            return None

    @property
    def dreg_mag_raw_time(self):
        """
        Contains time at which the last magnetometer data from the magnetometer was acquired.
        Payload structure:
        [31:0]  : MAG_RAW_TIME -- 32-bit IEEE Floating Point Value
        :return:  MAG_RAW_TIME as float; 
        """
        addr = 0x5E
        ok, payload = self.read_register(addr)
        if ok:
            mag_raw_time = struct.unpack('>f', payload[0:4])
            return mag_raw_time
        else:
            return None

    @property
    def dreg_temperature(self):
        """
        Contains the temperature output of the onboard temperature sensor.
        Payload structure:
        [31:0]  : TEMPERATURE -- Temperature in degrees Celcius (32-bit IEEE Floating Point)
        :return:  TEMPERATURE as float; 
        """
        addr = 0x5F
        ok, payload = self.read_register(addr)
        if ok:
            temperature = struct.unpack('>f', payload[0:4])
            return temperature
        else:
            return None

    @property
    def dreg_temperature_time(self):
        """
        Contains time at which the last temperature was acquired.
        Payload structure:
        [31:0]  : TEMPERATURE_TIME -- 32-bit IEEE Floating Point Value
        :return:  TEMPERATURE_TIME as float; 
        """
        addr = 0x60
        ok, payload = self.read_register(addr)
        if ok:
            temperature_time = struct.unpack('>f', payload[0:4])
            return temperature_time
        else:
            return None

    @property
    def dreg_gyro_proc_x(self):
        """
        Contains the actual measured angular rate from the gyro for the x axis in degrees/sec after calibration has
        been applied.
        Payload structure:
        [31:0]  : GYRO_PROC_X -- Gyro X in degrees / sec (32-bit IEEE Floating Point Value)
        :return:  GYRO_PROC_X as float; 
        """
        addr = 0x61
        ok, payload = self.read_register(addr)
        if ok:
            gyro_proc_x = struct.unpack('>f', payload[0:4])
            return gyro_proc_x
        else:
            return None

    @property
    def dreg_gyro_proc_y(self):
        """
        Contains the actual measured angular rate from the gyro for the y axis in degrees/sec after calibration has
        been applied.
        Payload structure:
        [31:0]  : GYRO_PROC_Y -- Gyro Y in degrees / sec (32-bit IEEE Floating Point Value)
        :return:  GYRO_PROC_Y as float; 
        """
        addr = 0x62
        ok, payload = self.read_register(addr)
        if ok:
            gyro_proc_y = struct.unpack('>f', payload[0:4])
            return gyro_proc_y
        else:
            return None

    @property
    def dreg_gyro_proc_z(self):
        """
        Contains the actual measured angular rate from the gyro for the z axis in degrees/sec after calibration has
        been applied.
        Payload structure:
        [31:0]  : GYRO_PROC_Z -- Gyro Z in degrees / sec (32-bit IEEE Floating Point Value)
        :return:  GYRO_PROC_Z as float; 
        """
        addr = 0x63
        ok, payload = self.read_register(addr)
        if ok:
            gyro_proc_z = struct.unpack('>f', payload[0:4])
            return gyro_proc_z
        else:
            return None

    @property
    def dreg_gyro_proc_time(self):
        """
        Contains the time at which the last rate gyro data from the gyro was measured.
        Payload structure:
        [31:0]  : GYRO_PROC_TIME -- Gyro time stamp (32-bit IEEE Floating Point Value)
        :return:  GYRO_PROC_TIME as float; 
        """
        addr = 0x64
        ok, payload = self.read_register(addr)
        if ok:
            gyro_proc_time = struct.unpack('>f', payload[0:4])
            return gyro_proc_time
        else:
            return None

    @property
    def dreg_accel_proc_x(self):
        """
        Contains the actual measured acceleration from the accelerometer for the x axis in m/s2 after calibration has
        been applied.
        Payload structure:
        [31:0]  : ACCEL_PROC_X -- Acceleration X in m/s2 (32-bit IEEE Floating Point Value)
        :return:  ACCEL_PROC_X as float; 
        """
        addr = 0x65
        ok, payload = self.read_register(addr)
        if ok:
            accel_proc_x = struct.unpack('>f', payload[0:4])
            return accel_proc_x
        else:
            return None

    @property
    def dreg_accel_proc_y(self):
        """
        Contains the actual measured acceleration from the accelerometer for the y axis in m/s2 after calibration has
        been applied.
        Payload structure:
        [31:0]  : ACCEL_PROC_Y -- Acceleration Y in m/s2 (32-bit IEEE Floating Point Value)
        :return:  ACCEL_PROC_Y as float; 
        """
        addr = 0x66
        ok, payload = self.read_register(addr)
        if ok:
            accel_proc_y = struct.unpack('>f', payload[0:4])
            return accel_proc_y
        else:
            return None

    @property
    def dreg_accel_proc_z(self):
        """
        Contains the actual measured acceleration from the accelerometer for the z axis in m/s2 after calibration has
        been applied.
        Payload structure:
        [31:0]  : ACCEL_PROC_Z -- Acceleration Z in m/s2 (32-bit IEEE Floating Point Value)
        :return:  ACCEL_PROC_Z as float; 
        """
        addr = 0x67
        ok, payload = self.read_register(addr)
        if ok:
            accel_proc_z = struct.unpack('>f', payload[0:4])
            return accel_proc_z
        else:
            return None

    @property
    def dreg_accel_proc_time(self):
        """
        Contains the time at which the last acceleration data from the accelerometer was measured.
        Payload structure:
        [31:0]  : ACCEL_PROC_TIME -- Accelerometer time stamp (32-bit IEEE Floating Point Value)
        :return:  ACCEL_PROC_TIME as float; 
        """
        addr = 0x68
        ok, payload = self.read_register(addr)
        if ok:
            accel_proc_time = struct.unpack('>f', payload[0:4])
            return accel_proc_time
        else:
            return None

    @property
    def dreg_mag_proc_x(self):
        """
        Contains the actual measured magnetic field from the magnetometer for the x axis after calibration has been
        applied.
        Payload structure:
        [31:0]  : MAG_PROC_X -- Magnetometer X (32-bit IEEE Floating Point Value)
        :return:  MAG_PROC_X as float; 
        """
        addr = 0x69
        ok, payload = self.read_register(addr)
        if ok:
            mag_proc_x = struct.unpack('>f', payload[0:4])
            return mag_proc_x
        else:
            return None

    @property
    def dreg_mag_proc_y(self):
        """
        Contains the actual measured magnetic field from the magnetometer for the y axis after calibration has been
        applied.
        Payload structure:
        [31:0]  : MAG_PROC_Y -- Magnetometer Y (32-bit IEEE Floating Point Value)
        :return:  MAG_PROC_Y as float; 
        """
        addr = 0x6A
        ok, payload = self.read_register(addr)
        if ok:
            mag_proc_y = struct.unpack('>f', payload[0:4])
            return mag_proc_y
        else:
            return None

    @property
    def dreg_mag_proc_z(self):
        """
        Contains the actual measured magnetic field from the magnetometer for the z axis after calibration has been
        applied.
        Payload structure:
        [31:0]  : MAG_PROC_Z -- Magnetometer Z (32-bit IEEE Floating Point Value)
        :return:  MAG_PROC_Z as float; 
        """
        addr = 0x6B
        ok, payload = self.read_register(addr)
        if ok:
            mag_proc_z = struct.unpack('>f', payload[0:4])
            return mag_proc_z
        else:
            return None

    @property
    def dreg_mag_proc_time(self):
        """
        Contains the time stamp at which the calibrated magnetometer data was acquired.
        Payload structure:
        [31:0]  : MAG_PROC_TIME -- Magnetometer time stamp (32-bit IEEE Floating Point Value)
        :return:  MAG_PROC_TIME as float; 
        """
        addr = 0x6C
        ok, payload = self.read_register(addr)
        if ok:
            mag_proc_time = struct.unpack('>f', payload[0:4])
            return mag_proc_time
        else:
            return None

    @property
    def dreg_quat_ab(self):
        """
        Contains the first two components (a and b) of the estimated quaternion attitude.
        Payload structure:
        [31:16] : QUAT_A -- First quaternion component. Stored as a 16-bit signed integer. To get the actual value, divide by 29789.09091.
        [15:0]  : QUAT_B -- Second quaternion component. Stored as a 16-bit signed integer. To get the actual value, divide by 29789.09091.
        :return:  QUAT_A as int16_t; QUAT_B as int16_t; 
        """
        addr = 0x6D
        ok, payload = self.read_register(addr)
        if ok:
            quat_a, quat_b = struct.unpack('>hh', payload[0:4])
            return quat_a, quat_b
        else:
            return None

    @property
    def dreg_quat_cd(self):
        """
        Contains the second two components (c and d) of the estimated quaternion attitude.
        Payload structure:
        [31:16] : QUAT_C -- Third quaternion component. Stored as a 16-bit signed integer. To get the actual value, divide by 29789.09091.
        [15:0]  : QUAT_D -- Fourth quaternion component. Stored as a 16-bit signed integer. To get the actual value, divide by 29789.09091.
        :return:  QUAT_C as int16_t; QUAT_D as int16_t; 
        """
        addr = 0x6E
        ok, payload = self.read_register(addr)
        if ok:
            quat_c, quat_d = struct.unpack('>hh', payload[0:4])
            return quat_c, quat_d
        else:
            return None

    @property
    def dreg_quat_time(self):
        """
        Contains the time that the quaternion attitude was estimated.
        Payload structure:
        [31:0]  : QUAT_TIME -- Quaternion time (32-bit IEEE Floating Point Value)
        :return:  QUAT_TIME as float; 
        """
        addr = 0x6F
        ok, payload = self.read_register(addr)
        if ok:
            quat_time = struct.unpack('>f', payload[0:4])
            return quat_time
        else:
            return None

    @property
    def dreg_euler_phi_theta(self):
        """
        Contains the pitch and roll angle estimates.
        Payload structure:
        [31:16] : PHI -- Roll angle. Stored as a 16-bit signed integer. To get the actual value, divide by 91.02222.
        [15:0]  : THETA -- Pitch angle. Stored as a 16-bit signed integer. To get the actual value, divide by 91.02222.
        :return:  PHI as int16_t; THETA as int16_t; 
        """
        addr = 0x70
        ok, payload = self.read_register(addr)
        if ok:
            phi, theta = struct.unpack('>hh', payload[0:4])
            return phi, theta
        else:
            return None

    @property
    def dreg_euler_psi(self):
        """
        Contains the yaw angle estimate.
        Payload structure:
        [31:16] : PSI -- Yaw angle. Stored as a 16-bit signed integer. To get the actual value, divide by 91.02222.
        :return:  PSI as int16_t; 
        """
        addr = 0x71
        ok, payload = self.read_register(addr)
        if ok:
            psi = struct.unpack('>hxx', payload[0:4])
            return psi
        else:
            return None

    @property
    def dreg_euler_phi_theta_dot(self):
        """
        Contains the pitch and roll rate estimates.
        Payload structure:
        [31:16] : PHI_DOT -- Roll rate. Stored as a 16-bit signed integer. To get the actual value, divide by 16.0.
        [15:0]  : THETA_DOT -- Pitch rate. Stored as a 16-bit signed integer. To get the actual value, divide by 16.0.
        :return:  PHI_DOT as int16_t; THETA_DOT as int16_t; 
        """
        addr = 0x72
        ok, payload = self.read_register(addr)
        if ok:
            phi_dot, theta_dot = struct.unpack('>hh', payload[0:4])
            return phi_dot, theta_dot
        else:
            return None

    @property
    def dreg_euler_psi_dot(self):
        """
        Contains the yaw rate estimate.
        Payload structure:
        [31:16] : PSI_DOT -- Yaw rate. Stored as a 16-bit signed integer. To get the actual value, divide by 16.0.
        :return:  PSI_DOT as int16_t; 
        """
        addr = 0x73
        ok, payload = self.read_register(addr)
        if ok:
            psi_dot = struct.unpack('>hxx', payload[0:4])
            return psi_dot
        else:
            return None

    @property
    def dreg_euler_time(self):
        """
        Contains the time that the Euler Angles were estimated.
        Payload structure:
        [31:0]  : EULER_TIME -- Euler time (32-bit IEEE Floating Point Value)
        :return:  EULER_TIME as float; 
        """
        addr = 0x74
        ok, payload = self.read_register(addr)
        if ok:
            euler_time = struct.unpack('>f', payload[0:4])
            return euler_time
        else:
            return None

    @property
    def dreg_position_north(self):
        """
        Contains the measured north position in meters from the latitude specified in CREG_HOME_NORTH.
        Payload structure:
        [31:0]  : POSITION_NORTH -- North Position (32-bit IEEE Floating Point Value)
        :return:  POSITION_NORTH as float; 
        """
        addr = 0x75
        ok, payload = self.read_register(addr)
        if ok:
            position_north = struct.unpack('>f', payload[0:4])
            return position_north
        else:
            return None

    @property
    def dreg_position_east(self):
        """
        Contains the measured east position in meters from the longitude specified in CREG_HOME_EAST.
        Payload structure:
        [31:0]  : POSITION_EAST -- East Position (32-bit IEEE Floating Point Value)
        :return:  POSITION_EAST as float; 
        """
        addr = 0x76
        ok, payload = self.read_register(addr)
        if ok:
            position_east = struct.unpack('>f', payload[0:4])
            return position_east
        else:
            return None

    @property
    def dreg_position_up(self):
        """
        Contains the measured altitude in meters from the altitude specified in CREG_HOME_UP.
        Payload structure:
        [31:0]  : POSITION_UP -- Altitude (32-bit IEEE Floating Point Value)
        :return:  POSITION_UP as float; 
        """
        addr = 0x77
        ok, payload = self.read_register(addr)
        if ok:
            position_up = struct.unpack('>f', payload[0:4])
            return position_up
        else:
            return None

    @property
    def dreg_position_time(self):
        """
        Contains the time at which the position was acquired.
        Payload structure:
        [31:0]  : POSITION_TIME -- Position Time (32-bit IEEE Floating Point Value)
        :return:  POSITION_TIME as float; 
        """
        addr = 0x78
        ok, payload = self.read_register(addr)
        if ok:
            position_time = struct.unpack('>f', payload[0:4])
            return position_time
        else:
            return None

    @property
    def dreg_velocity_north(self):
        """
        Contains the measured north velocity in m/s.
        Payload structure:
        [31:0]  : VELOCITY_NORTH -- North Velocity (32-bit IEEE Floating Point Value)
        :return:  VELOCITY_NORTH as float; 
        """
        addr = 0x79
        ok, payload = self.read_register(addr)
        if ok:
            velocity_north = struct.unpack('>f', payload[0:4])
            return velocity_north
        else:
            return None

    @property
    def dreg_velocity_east(self):
        """
        Contains the measured east velocity in m/s.
        Payload structure:
        [31:0]  : VELOCITY_EAST -- East Velocity (32-bit IEEE Floating Point Value)
        :return:  VELOCITY_EAST as float; 
        """
        addr = 0x7A
        ok, payload = self.read_register(addr)
        if ok:
            velocity_east = struct.unpack('>f', payload[0:4])
            return velocity_east
        else:
            return None

    @property
    def dreg_velocity_up(self):
        """
        Contains the measured altitude velocity in m/s.
        Payload structure:
        [31:0]  : VELOCITY_UP -- Altitude Velocity (32-bit IEEE Floating Point Value)
        :return:  VELOCITY_UP as float; 
        """
        addr = 0x7B
        ok, payload = self.read_register(addr)
        if ok:
            velocity_up = struct.unpack('>f', payload[0:4])
            return velocity_up
        else:
            return None

    @property
    def dreg_velocity_time(self):
        """
        Contains the time at which the velocity was measured.
        Payload structure:
        [31:0]  : VELOCITY_TIME -- Velocity time (32-bit IEEE Floating Point Value)
        :return:  VELOCITY_TIME as float; 
        """
        addr = 0x7C
        ok, payload = self.read_register(addr)
        if ok:
            velocity_time = struct.unpack('>f', payload[0:4])
            return velocity_time
        else:
            return None

    @property
    def dreg_gps_latitude(self):
        """
        Contains the GPS-reported latitude in degrees.
        Payload structure:
        [31:0]  : GPS_LATITUDE -- GPS Latitude (32-bit IEEE Floating Point Value)
        :return:  GPS_LATITUDE as float; 
        """
        addr = 0x7D
        ok, payload = self.read_register(addr)
        if ok:
            gps_latitude = struct.unpack('>f', payload[0:4])
            return gps_latitude
        else:
            return None

    @property
    def dreg_gps_longitude(self):
        """
        Contains the GPS-reported longitude in degrees.
        Payload structure:
        [31:0]  : GPS_LONGITUDE -- GPS Longitude (32-bit IEEE Floating Point Value)
        :return:  GPS_LONGITUDE as float; 
        """
        addr = 0x7E
        ok, payload = self.read_register(addr)
        if ok:
            gps_longitude = struct.unpack('>f', payload[0:4])
            return gps_longitude
        else:
            return None

    @property
    def dreg_gps_altitude(self):
        """
        Contains the GPS-reported altitude in meters.
        Payload structure:
        [31:0]  : GPS_ALTITUDE -- GPS Altitude (32-bit IEEE Floating Point Value)
        :return:  GPS_ALTITUDE as float; 
        """
        addr = 0x7F
        ok, payload = self.read_register(addr)
        if ok:
            gps_altitude = struct.unpack('>f', payload[0:4])
            return gps_altitude
        else:
            return None

    @property
    def dreg_gps_course(self):
        """
        Contains the GPS-reported course in degrees.
        Payload structure:
        [31:0]  : GPS_COURSE -- GPS Course (32-bit IEEE Floating Point Value)
        :return:  GPS_COURSE as float; 
        """
        addr = 0x80
        ok, payload = self.read_register(addr)
        if ok:
            gps_course = struct.unpack('>f', payload[0:4])
            return gps_course
        else:
            return None

    @property
    def dreg_gps_speed(self):
        """
        Contains the GPS-reported speed in m/s.
        Payload structure:
        [31:0]  : GPS_SPEED -- GPS Speed (32-bit IEEE Floating Point Value)
        :return:  GPS_SPEED as float; 
        """
        addr = 0x81
        ok, payload = self.read_register(addr)
        if ok:
            gps_speed = struct.unpack('>f', payload[0:4])
            return gps_speed
        else:
            return None

    @property
    def dreg_gps_time(self):
        """
        Contains the GPS-reported time in seconds from the last epoch.
        Payload structure:
        [31:0]  : GPS_TIME -- GPS Speed (32-bit IEEE Floating Point Value)
        :return:  GPS_TIME as float; 
        """
        addr = 0x82
        ok, payload = self.read_register(addr)
        if ok:
            gps_time = struct.unpack('>f', payload[0:4])
            return gps_time
        else:
            return None

    @property
    def dreg_gps_sat_1_2(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 1 and 2.
        Payload structure:
        [31:24] : SAT_1_ID -- Satellite 1 ID
        [23:16] : SAT_1_SNR -- Signal-to-Noise Ratio of satellite 1 as reported by GPS receiver.
        [15:8]  : SAT_2_ID -- Satellite 2 ID
        [7:0]   : SAT_2_SNR -- Signal-to-Noise Ratio of satellite 2 as reported by GPS receiver.
        :return:  SAT_1_ID as uint8_t; SAT_1_SNR as uint8_t; SAT_2_ID as uint8_t; SAT_2_SNR as uint8_t; 
        """
        addr = 0x83
        ok, payload = self.read_register(addr)
        if ok:
            sat_1_id, sat_1_snr, sat_2_id, sat_2_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_1_id, sat_1_snr, sat_2_id, sat_2_snr
        else:
            return None

    @property
    def dreg_gps_sat_3_4(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 3 and 4.
        Payload structure:
        [31:24] : SAT_3_ID -- Satellite 3 ID
        [23:16] : SAT_3_SNR -- Signal-to-Noise Ratio of satellite 3 as reported by GPS receiver.
        [15:8]  : SAT_4_ID -- Satellite 4 ID
        [7:0]   : SAT_4_SNR -- Signal-to-Noise Ratio of satellite 4 as reported by GPS receiver.
        :return:  SAT_3_ID as uint8_t; SAT_3_SNR as uint8_t; SAT_4_ID as uint8_t; SAT_4_SNR as uint8_t; 
        """
        addr = 0x84
        ok, payload = self.read_register(addr)
        if ok:
            sat_3_id, sat_3_snr, sat_4_id, sat_4_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_3_id, sat_3_snr, sat_4_id, sat_4_snr
        else:
            return None

    @property
    def dreg_gps_sat_5_6(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 5 and 6.
        Payload structure:
        [31:24] : SAT_5_ID -- Satellite 5 ID
        [23:16] : SAT_5_SNR -- Signal-to-Noise Ratio of satellite 5 as reported by GPS receiver.
        [15:8]  : SAT_6_ID -- Satellite 6 ID
        [7:0]   : SAT_6_SNR -- Signal-to-Noise Ratio of satellite 6 as reported by GPS receiver.
        :return:  SAT_5_ID as uint8_t; SAT_5_SNR as uint8_t; SAT_6_ID as uint8_t; SAT_6_SNR as uint8_t; 
        """
        addr = 0x85
        ok, payload = self.read_register(addr)
        if ok:
            sat_5_id, sat_5_snr, sat_6_id, sat_6_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_5_id, sat_5_snr, sat_6_id, sat_6_snr
        else:
            return None

    @property
    def dreg_gps_sat_7_8(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 7 and 8.
        Payload structure:
        [31:24] : SAT_7_ID -- Satellite 7 ID
        [23:16] : SAT_7_SNR -- Signal-to-Noise Ratio of satellite 7 as reported by GPS receiver.
        [15:8]  : SAT_8_ID -- Satellite 8 ID
        [7:0]   : SAT_8_SNR -- Signal-to-Noise Ratio of satellite 8 as reported by GPS receiver.
        :return:  SAT_7_ID as uint8_t; SAT_7_SNR as uint8_t; SAT_8_ID as uint8_t; SAT_8_SNR as uint8_t; 
        """
        addr = 0x86
        ok, payload = self.read_register(addr)
        if ok:
            sat_7_id, sat_7_snr, sat_8_id, sat_8_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_7_id, sat_7_snr, sat_8_id, sat_8_snr
        else:
            return None

    @property
    def dreg_gps_sat_9_10(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 9 and 10.
        Payload structure:
        [31:24] : SAT_9_ID -- Satellite 9 ID
        [23:16] : SAT_9_SNR -- Signal-to-Noise Ratio of satellite 9 as reported by GPS receiver.
        [15:8]  : SAT_10_ID -- Satellite 10 ID
        [7:0]   : SAT_10_SNR -- Signal-to-Noise Ratio of satellite 10 as reported by GPS receiver.
        :return:  SAT_9_ID as uint8_t; SAT_9_SNR as uint8_t; SAT_10_ID as uint8_t; SAT_10_SNR as uint8_t; 
        """
        addr = 0x87
        ok, payload = self.read_register(addr)
        if ok:
            sat_9_id, sat_9_snr, sat_10_id, sat_10_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_9_id, sat_9_snr, sat_10_id, sat_10_snr
        else:
            return None

    @property
    def dreg_gps_sat_11_12(self):
        """
        Contains satellite ID and signal-to-noise ratio (SNR) for satellites 11 and 12.
        Payload structure:
        [31:24] : SAT_11_ID -- Satellite 11 ID
        [23:16] : SAT_11_SNR -- Signal-to-Noise Ratio of satellite 11 as reported by GPS receiver.
        [15:8]  : SAT_12_ID -- Satellite 12 ID
        [7:0]   : SAT_12_SNR -- Signal-to-Noise Ratio of satellite 12 as reported by GPS receiver.
        :return:  SAT_11_ID as uint8_t; SAT_11_SNR as uint8_t; SAT_12_ID as uint8_t; SAT_12_SNR as uint8_t; 
        """
        addr = 0x88
        ok, payload = self.read_register(addr)
        if ok:
            sat_11_id, sat_11_snr, sat_12_id, sat_12_snr = struct.unpack('>BBBB', payload[0:4])
            return sat_11_id, sat_11_snr, sat_12_id, sat_12_snr
        else:
            return None

    @property
    def dreg_gyro_bias_x(self):
        """
        Contains the estimated x-axis bias for the gyro in degrees/s.
        Payload structure:
        [31:0]  : GYRO_BIAS_X -- Gyro bias X (32-bit IEEE Floating Point Value)
        :return:  GYRO_BIAS_X as float; 
        """
        addr = 0x89
        ok, payload = self.read_register(addr)
        if ok:
            gyro_bias_x = struct.unpack('>f', payload[0:4])
            return gyro_bias_x
        else:
            return None

    @property
    def dreg_gyro_bias_y(self):
        """
        Contains the estimated y-axis bias for the gyro in degrees/s.
        Payload structure:
        [31:0]  : GYRO_BIAS_Y -- Gyro bias Y (32-bit IEEE Floating Point Value)
        :return:  GYRO_BIAS_Y as float; 
        """
        addr = 0x8A
        ok, payload = self.read_register(addr)
        if ok:
            gyro_bias_y = struct.unpack('>f', payload[0:4])
            return gyro_bias_y
        else:
            return None

    @property
    def dreg_gyro_bias_z(self):
        """
        Contains the estimated z-axis bias for the gyro in degrees/s.
        Payload structure:
        [31:0]  : GYRO_BIAS_Z -- Gyro bias Z (32-bit IEEE Floating Point Value)
        :return:  GYRO_BIAS_Z as float; 
        """
        addr = 0x8B
        ok, payload = self.read_register(addr)
        if ok:
            gyro_bias_z = struct.unpack('>f', payload[0:4])
            return gyro_bias_z
        else:
            return None

    @property
    def get_fw_revision(self):
        """
        Firmware build identification string: a four byte ASCII character sequence which corresponds to a firmware
        series.
        Payload structure:
        [31:0]  : FW_REVISION -- Firmware revision string
        :return:  FW_REVISION as string; 
        """
        addr = 0xAA
        ok, payload = self.read_register(addr)
        if ok:
            fw_revision = struct.unpack('>4s', payload[0:4])[0].decode('utf-8')
            return fw_revision
        else:
            return None

    @property
    def flash_commit(self):
        raise RuntimeError('flash_commit has no getter! The register flash_commit is write-only!')

    @flash_commit.setter
    def flash_commit(self, new_value):
        addr = 0xAB
        self.write_register(addr, new_value)

    @property
    def reset_to_factory(self):
        raise RuntimeError('reset_to_factory has no getter! The register reset_to_factory is write-only!')

    @reset_to_factory.setter
    def reset_to_factory(self, new_value):
        addr = 0xAC
        self.write_register(addr, new_value)

    @property
    def zero_gyros(self):
        raise RuntimeError('zero_gyros has no getter! The register zero_gyros is write-only!')

    @zero_gyros.setter
    def zero_gyros(self, new_value):
        addr = 0xAD
        self.write_register(addr, new_value)

    @property
    def set_home_position(self):
        raise RuntimeError('set_home_position has no getter! The register set_home_position is write-only!')

    @set_home_position.setter
    def set_home_position(self, new_value):
        addr = 0xAE
        self.write_register(addr, new_value)

    @property
    def set_mag_reference(self):
        raise RuntimeError('set_mag_reference has no getter! The register set_mag_reference is write-only!')

    @set_mag_reference.setter
    def set_mag_reference(self, new_value):
        addr = 0xB0
        self.write_register(addr, new_value)

    @property
    def calibrate_accelerometers(self):
        raise RuntimeError('calibrate_accelerometers has no getter! The register calibrate_accelerometers is write-only!')

    @calibrate_accelerometers.setter
    def calibrate_accelerometers(self, new_value):
        addr = 0xB1
        self.write_register(addr, new_value)

    @property
    def reset_ekf(self):
        raise RuntimeError('reset_ekf has no getter! The register reset_ekf is write-only!')

    @reset_ekf.setter
    def reset_ekf(self, new_value):
        addr = 0xB3
        self.write_register(addr, new_value)


    @property
    def hidden_gyro_variance(self):
        """
        Gyro variance
        Payload structure:
        [31:0]  : GYRO_VARIANCE -- Gyro variance for EKF
        :return:  GYRO_VARIANCE as float; 
        """
        addr = 0x00
        ok, payload = self.read_register(addr, hidden=True)
        if ok:
            gyro_variance = struct.unpack('>f', payload[0:4])
            return gyro_variance
        else:
            return None

    @hidden_gyro_variance.setter
    def hidden_gyro_variance(self, new_value):
        addr = 0x00
        self.write_register(addr, new_value, hidden=True)

    @property
    def hidden_accel_variance(self):
        """
        Accelerometer variance
        Payload structure:
        [31:0]  : ACCEL_VARIANCE -- Accelerometer variance IEEE floating point value.
        :return:  ACCEL_VARIANCE as float; 
        """
        addr = 0x01
        ok, payload = self.read_register(addr, hidden=True)
        if ok:
            accel_variance = struct.unpack('>f', payload[0:4])
            return accel_variance
        else:
            return None

    @hidden_accel_variance.setter
    def hidden_accel_variance(self, new_value):
        addr = 0x01
        self.write_register(addr, new_value, hidden=True)


if __name__ == '__main__':
    pass
