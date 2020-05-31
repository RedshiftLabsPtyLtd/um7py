#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# Date: 2 March 2020
# Version: v0.1
# License: MIT

import json
import logging
import os
import os.path
import serial
import struct
import sys

from time import monotonic
from typing import Tuple, List, Dict, Any, Union, Callable

from um7py.um7_broadcast_packets import UM7AllRawPacket, UM7HealthPacket, UM7GyroBiasPacket, UM7ProcMagPacket, \
    UM7ProcGyroPacket, UM7ProcAccelPacket, UM7RawMagPacket, UM7RawGyroPacket, UM7RawAccelPacket, UM7QuaternionPacket, \
    UM7EulerPacket, UM7AllProcPacket
from um7py.um7_registers import UM7Registers


class RslException(Exception):
    """
    RSL Exception class for recording RedShiftLabs and/or UM7 specific errors
    """
    pass


class UM7Serial(UM7Registers):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_file = kwargs.get('device')
        self.device_dict = None
        self.port = serial.Serial()
        self.port_name = None
        self.port_config = None
        self.buffer = bytes()
        self.buffer_size = 125
        self.firmware_version = None
        self.uid_32_bit = None
        if kwargs.get('port_name') is not None:
            self.port_name = kwargs.get('port_name')
        else:
            port_found = self.find_port()
            if not port_found:
                raise RslException("Device specified in the config is not connected!")
        self.init_connection()

    def init_connection(self):
        self.port = serial.Serial(port=self.port_name)
        self.port.port = self.port_name
        self.port.baudrate = 115200
        if not self.port.is_open:
            self.port.open()

    def connect(self, *args, **kwargs):
        self.init_connection()

    def find_port(self):
        if not self.device_file:
            raise RslException("No configuration file specified!")
        if not os.path.isfile(self.device_file):
            src_path = os.path.dirname(__file__)
            guessing_file_path = os.path.join(src_path, self.device_file)
            if not os.path.isfile(guessing_file_path):
                raise RslException(f"Specify absolute path to the `device` json file, cannot find {self.device_file}")
            else:
                self.device_file = guessing_file_path
        with open(self.device_file) as fp:
            self.device_dict = json.load(fp)
        # go through each device and match vendor, then key
        if sys.platform.startswith('win32'):
            from serial.tools import list_ports
            device_list = list_ports.comports()
            for device in device_list:
                json_config = {}
                # go through device list and check each FTDI device for a match
                if device.manufacturer == "FTDI":
                    json_config['ID_VENDOR'] = device.manufacturer
                    json_config['ID_SERIAL_SHORT'] = device.serial_number
                    # don't know what the model should look like so were making it "pid:vid". 
                    # This matches the windows section of the autodetect script
                    json_config['ID_MODEL'] = '{0:04x}:{1:04x}'.format(device.vid, device.pid)
                    if self.device_dict == json_config:
                        self.port_name = device.device   # set serial port ("COM4", for example)
                        return True
            else:
                return False
        else:
            import pyudev
            context = pyudev.Context()
            for device in context.list_devices(subsystem='tty'):
                json_config = {}
                if device.get('ID_VENDOR') == 'FTDI':
                    for key in self.device_dict:
                        json_config[key] = device.get(key)
                    if self.device_dict == json_config:
                        self.port_name = device.device_node
                        return True
            else:
                return False

    def get_preamble(self):
        preamble = bytes('snp', encoding='ascii')
        return preamble

    def compute_checksum(self, partial_packet: bytes) -> bytes:
        checksum = 0
        for byte in partial_packet:
            checksum += byte
        checksum_bytes = int.to_bytes(checksum, length=2, byteorder='big', signed=False)
        return checksum_bytes

    def construct_packet_type(self, has_data: bool = False, is_batch: bool = False, data_length: int = 0,
                              hidden: bool = False, command_failed: bool = False) -> int:
        if data_length > 15:
            raise RslException(f"Batch size for command should not exceed 15, but got {data_length}")
        packet_type = has_data << 7 | is_batch << 6 | data_length << 2 | hidden << 1 | command_failed
        return packet_type

    def get_packet_type(self, extracted_packet_type: int) -> Tuple[bool, bool, int, bool, bool]:
        has_data = bool(extracted_packet_type >> 7 & 0x01)
        is_batch = bool(extracted_packet_type >> 6 & 0x01)
        batch_length = extracted_packet_type >> 2 & 0x0F
        hidden = bool(extracted_packet_type >> 1 & 0x01)
        command_failed = bool(extracted_packet_type & 0x01)
        return has_data, is_batch, batch_length, hidden, command_failed

    def construct_packet(self, packet_type: int, address: int, payload: bytes = bytes()) -> bytes:
        preamble = self.get_preamble()
        packet_type_byte = int.to_bytes(packet_type, length=1, byteorder='big')
        address_byte = int.to_bytes(address, length=1, byteorder='big')
        partial_packet = preamble + packet_type_byte + address_byte + payload
        checksum = self.compute_checksum(partial_packet)
        packet = partial_packet + checksum
        return packet

    def send(self, packet: bytes) -> bool:
        bytes_written = self.port.write(packet)
        self.port.flush()
        return bytes_written == len(packet)

    def recv(self) -> Tuple[bool, bytes]:
        ok = False
        while not ok:
            # read until we get something in the buffer
            in_waiting = self.port.in_waiting
            logging.info(f"waiting buffer: {in_waiting}")
            self.buffer += self.port.read(self.buffer_size)
            # self.buffer += self.port.read(in_waiting)
            logging.info(f"buffer size: {len(self.buffer)}")
            # self.__buffer = self.__port.read(self.__port.inWaiting()) # causes too long of a delay
            ok = len(self.buffer) > 0
        return True, self.buffer

    def send_recv(self, packet: bytes) -> bytes:
        send_ok = self.send(packet)
        if not send_ok:
            raise RslException("Sending packet failed!")
        recv_ok, _ = self.recv()
        if not recv_ok:
            raise RslException("Receiving packet failed!")
        return self.buffer

    def find_packet(self, sensor_response: bytes) -> Tuple[bytes, bytes]:
        preamble = self.get_preamble()
        packet_start_idx = sensor_response.find(preamble)

        if packet_start_idx == -1:
            # preamble of packet not found, exit
            return bytes(), bytes()

        next_packet_rel_idx = sensor_response[packet_start_idx+3:].find(preamble)
        next_packet_start_idx = packet_start_idx + 3 + next_packet_rel_idx

        if next_packet_start_idx == -1:
            # preamble of next packet not found, exit
            return bytes(), bytes()

        # complete packet found in data
        packet = sensor_response[packet_start_idx:next_packet_start_idx]
        remainder = sensor_response[next_packet_start_idx:]
        return packet, remainder

    def find_response(self, reg_addr: int, hidden: bool = False, expected_length: int = 7) -> Tuple[bool, bytes]:
        while len(self.buffer) > 0:
            packet, self.buffer = self.find_packet(self.buffer)
            if len(packet) < 4:
                return False, bytes()
            logging.debug(f"{packet}")
            logging.debug(f"addr: {packet[4]}")
            packet_type = packet[3]
            is_packet_hidden = bool((packet_type >> 1) & 0x01)
            response_addr = packet[4]
            if response_addr == reg_addr and hidden == is_packet_hidden and len(packet) == expected_length:
                # required packet found
                return True, packet
        else:
            return False, bytes()

    def verify_checksum(self, packet: bytes) -> bool:
        computed_checksum = 0
        for byte in packet[:-2]:
            computed_checksum += byte
        received_checksum = int.from_bytes(packet[-2:], byteorder='big', signed=False)
        return computed_checksum == received_checksum

    def get_payload(self, packet: bytes) -> Tuple[bool, bytes]:
        ok = self.verify_checksum(packet)
        if not ok:
            raise RslException("Packet checksum INVALID!")
        return True, packet[5:-2]

    def check_packet(self, packet: bytes) -> bool:
        packet_type = packet[3]
        has_data = bool((packet_type >> 7) & 0x01)
        is_batch = bool((packet_type >> 6) & 0x01)
        data_len = (packet_type >> 2) & 0x0F
        hidden = bool((packet_type >> 1) & 0x01)
        error = packet_type & 0x01
        if error:
            logging.error(f"Error bit set for packet: {packet}!")
            return False
        elif not has_data and len(packet) != 7:
            logging.error(f"Packet without data (has_data = 0) shall have 7 bytes, got {len(packet)}")
            return False
        elif has_data and data_len == 0 and len(packet) != 11:
            logging.error(f"Single packet has 4 bytes payload, in total 11 bytes, got {len(packet)}")
            return False
        elif has_data and data_len > 0 and len(packet) != 7 + 4 * data_len:
            logging.error(f"Batch packet with data_len {data_len} shall be {7 + 4 * data_len} bytes, got {len(packet)}")
            return False
        else:
            # all the checks pass then
            return True

    def read_register(self, reg_addr: int, hidden: bool = False) -> Tuple[bool, bytes]:
        packet_type = self.construct_packet_type(hidden=hidden)
        packet_to_send = self.construct_packet(packet_type, reg_addr)
        logging.debug(f"packet sent: {packet_to_send}")
        self.send_recv(packet_to_send)
        t = monotonic()
        ok, sensor_reply = self.find_response(reg_addr, hidden, 11)
        if ok:
            logging.debug(f"packet: {sensor_reply}")
            self.check_packet(sensor_reply)
            ok, payload = self.get_payload(sensor_reply)
            return ok, payload
        else:
            while monotonic() - t < 0.2:
                # try to send <-> receive packets for a pre-defined time out time
                self.send_recv(packet_to_send)
                ok, sensor_reply = self.find_response(reg_addr, hidden, 11)
                if ok and len(sensor_reply) > 7:
                    logging.debug(f"packet: {sensor_reply}")
                    self.check_packet(sensor_reply)
                    ok, payload = self.get_payload(sensor_reply)
                    return ok, payload
            return False, bytes()

    def write_register(self, reg_addr: int, reg_value: Union[int, bytes, float], hidden: bool = False) -> bool:
        packet_type = self.construct_packet_type(has_data=True, hidden=hidden)
        if type(reg_value) == int:
            payload = int.to_bytes(reg_value, byteorder='big', length=4)
        elif type(reg_value) == bytes:
            payload = reg_value
        elif type(reg_value) == float:
            payload = struct.pack('>f', reg_value)
        packet_to_send = self.construct_packet(packet_type, reg_addr, payload)
        logging.debug(f"packet sent: {packet_to_send}")
        self.send_recv(packet_to_send)
        ok, sensor_reply = self.find_response(reg_addr)
        if ok:
            logging.debug(f"packet: {sensor_reply}")
            self.check_packet(sensor_reply)
            ok, payload = self.get_payload(sensor_reply)
            return ok

    def recv_broadcast_packet(self, packet_target_addr: int, expected_packet_length: int,
                              decode_callback: Callable, num_packets: int = -1):
        received_packets = 0
        while num_packets == -1 or received_packets < num_packets:
            ok, _ = self.recv()
            while len(self.buffer) > 0:
                packet, self.buffer = self.find_packet(self.buffer)
                # logging.info(f"buffer length: {len(self.buffer)}")
                if len(packet) > 7:
                    recv_packet_addr = packet[4]
                    if recv_packet_addr == packet_target_addr:
                        packet_correct_length = len(packet) == expected_packet_length
                        if not packet_correct_length:
                            logging.error(f"Invalid packet length for addr: {packet_target_addr}, "
                                          f"expected: {expected_packet_length}, got: {len(packet)}, packet: {packet}")
                        checksum_ok = self.verify_checksum(packet)
                        if not checksum_ok:
                            logging.error(f"Checksum failed for broadcast packet with addr: {packet_target_addr}")
                        packet_type_check_ok = self.check_packet(packet)
                        if not packet_type_check_ok:
                            logging.error(f"Checking packet type failed for broadcast with addr: {packet_target_addr}!")
                        if packet_correct_length and checksum_ok and packet_type_check_ok:
                            yield decode_callback(packet)
                            received_packets += 1

    def recv_all_raw_broadcast(self, num_packets: int = -1):
        all_raw_start_addr = self.svd_parser.find_register_by(name='DREG_GYRO_RAW_XY').address
        broadcast_packet_length = 51
        return self.recv_broadcast_packet(all_raw_start_addr, broadcast_packet_length,
                                          self.decode_all_raw_broadcast, num_packets)

    def recv_all_proc_broadcast(self, num_packets: int = -1):
        all_proc_start_addr = self.svd_parser.find_register_by(name='DREG_GYRO_PROC_X').address
        broadcast_packet_length = 55
        return self.recv_broadcast_packet(all_proc_start_addr, broadcast_packet_length,
                                          self.decode_all_proc_broadcast, num_packets)

    def recv_euler_broadcast(self, num_packets: int = -1):
        euler_start_addr = self.svd_parser.find_register_by(name='DREG_EULER_PHI_THETA').address
        broadcast_packet_length = 27
        return self.recv_broadcast_packet(euler_start_addr, broadcast_packet_length,
                                          self.decode_euler_broadcast, num_packets)

    def recv_quaternion_broadcast(self, num_packets: int = -1):
        quat_start_addr = self.svd_parser.find_register_by(name='DREG_QUAT_AB').address
        broadcast_packet_length = 19
        return self.recv_broadcast_packet(quat_start_addr, broadcast_packet_length,
                                          self.decode_quaternion_broadcast, num_packets)

    def recv_health_broadcast(self, num_packets: int = -1):
        health_start_addr = self.svd_parser.find_register_by(name='DREG_HEALTH').address
        broadcast_packet_length = 11
        return self.recv_broadcast_packet(health_start_addr, broadcast_packet_length,
                                          self.decode_health_broadcast, num_packets)

    def recv_raw_accel_broadcast(self, num_packets: int = -1):
        raw_accel_1_addr = self.svd_parser.find_register_by(name='DREG_ACCEL_RAW_XY').address
        broadcast_packet_length = 19
        return self.recv_broadcast_packet(raw_accel_1_addr, broadcast_packet_length,
                                          self.decode_raw_accel_broadcast, num_packets)

    def recv_raw_gyro_broadcast(self, num_packets: int = -1):
        raw_gyro_1_addr = self.svd_parser.find_register_by(name='DREG_GYRO_RAW_XY').address
        broadcast_packet_length = 19
        return self.recv_broadcast_packet(raw_gyro_1_addr, broadcast_packet_length,
                                          self.decode_raw_gyro_broadcast, num_packets)

    def recv_raw_mag_broadcast(self, num_packets: int = -1):
        raw_mag_1_addr = self.svd_parser.find_register_by(name='DREG_MAG_RAW_XY').address
        broadcast_packet_length = 19
        return self.recv_broadcast_packet(raw_mag_1_addr, broadcast_packet_length,
                                          self.decode_raw_mag_broadcast, num_packets)

    def recv_proc_accel_broadcast(self, num_packets: int = -1):
        proc_accel_1_addr = self.svd_parser.find_register_by(name='DREG_ACCEL_PROC_X').address
        broadcast_packet_length = 23
        return self.recv_broadcast_packet(proc_accel_1_addr, broadcast_packet_length,
                                          self.decode_proc_accel_broadcast, num_packets)

    def recv_proc_gyro_broadcast(self, num_packets: int = -1):
        proc_gyro_1_addr = self.svd_parser.find_register_by(name='DREG_GYRO_PROC_X').address
        broadcast_packet_length = 23
        return self.recv_broadcast_packet(proc_gyro_1_addr, broadcast_packet_length,
                                          self.decode_proc_gyro_broadcast, num_packets)

    def recv_proc_mag_broadcast(self, num_packets: int = -1):
        proc_mag_1_addr = self.svd_parser.find_register_by(name='DREG_MAG_PROC_X').address
        broadcast_packet_length = 23
        return self.recv_broadcast_packet(proc_mag_1_addr, broadcast_packet_length,
                                          self.decode_proc_mag_broadcast, num_packets)

    def recv_broadcast(self,  num_packets: int = -1):
        received_packets = 0
        while num_packets == -1 or received_packets < num_packets:
            ok, _ = self.recv()
            while len(self.buffer) > 0:
                packet, self.buffer = self.find_packet(self.buffer)
                if len(packet) > 7:
                    packet_addr = packet[4]
                    start_reg = self.svd_parser.find_register_by(address=packet_addr)
                    checksum_ok = self.verify_checksum(packet)
                    if not checksum_ok:
                        logging.error(f"Checksum failed for broadcast packet with start_reg: {start_reg}")
                    packet_type_check_ok = self.check_packet(packet)
                    if not packet_type_check_ok:
                        logging.error(f"Checking packet type failed for broadcast with start_reg: {start_reg}!")
                    health_start_addr = self.svd_parser.find_register_by(name='DREG_HEALTH').address
                    euler_start_addr = self.svd_parser.find_register_by(name='DREG_EULER_PHI_THETA').address
                    all_proc_start_addr = self.svd_parser.find_register_by(name='DREG_GYRO_PROC_X').address
                    accel_proc_start_addr = self.svd_parser.find_register_by(name='DREG_ACCEL_PROC_X').address
                    mag_proc_start_addr = self.svd_parser.find_register_by(name='DREG_MAG_PROC_X').address
                    all_raw_start_addr = self.svd_parser.find_register_by(name='DREG_GYRO_RAW_XY').address
                    accel_raw_start_addr = self.svd_parser.find_register_by(name='DREG_ACCEL_RAW_XY').address
                    mag_raw_start_addr = self.svd_parser.find_register_by(name='DREG_MAG_RAW_XY').address
                    gyro_bias_start_addr = self.svd_parser.find_register_by(name='DREG_GYRO_BIAS_X').address
                    quat_addr = self.svd_parser.find_register_by(name='DREG_QUAT_AB').address

                    if packet_addr == health_start_addr:
                        if len(packet) == 11:
                            logging.info("[HEALTH]: broadcast packet found!")
                            yield self.decode_health_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[HEALTH]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == euler_start_addr:
                        if len(packet) == 27:
                            logging.info("[EULER]: broadcast packet found!")
                            yield self.decode_euler_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[EULER]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == all_proc_start_addr:
                        if len(packet) == 55:
                            logging.info("[ALL_PROC]: broadcast packet found!")
                            yield self.decode_all_proc_broadcast(packet)
                            received_packets += 1
                        elif len(packet) == 23:
                            logging.info("[GYRO_PROC]: broadcast packet found!")
                            yield self.decode_proc_gyro_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[GYRO_PROC]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == accel_proc_start_addr:
                        if len(packet) == 23:
                            logging.info("[ACCEL_PROC]: broadcast packet found!")
                            yield self.decode_proc_accel_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[ACCEL_PROC]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == mag_proc_start_addr:
                        if len(packet) == 23:
                            logging.info("[MAG_PROC]: broadcast packet found!")
                            yield self.decode_proc_mag_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[MAG_PROC]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == all_raw_start_addr:
                        if len(packet) == 51:
                            logging.info("[ALL_RAW]: broadcast packet found!")
                            yield self.decode_all_raw_broadcast(packet)
                            received_packets += 1
                        elif len(packet) == 19:
                            logging.info("[GYRO_RAW]: broadcast packet found!")
                            yield self.decode_raw_gyro_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[GYRO_RAW]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == accel_raw_start_addr:
                        if len(packet) == 19:
                            logging.info("[ACCEL_RAW]: broadcast packet found!")
                            yield self.decode_raw_accel_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[ACCEL_RAW]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == mag_raw_start_addr:
                        if len(packet) == 23:
                            logging.info("[MAG_RAW]: broadcast packet found!")
                            yield self.decode_raw_mag_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[MAG_RAW]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == quat_addr:
                        if len(packet) == 19:
                            logging.info("[QUAT]: quaternion broadcast packet found!")
                            yield self.decode_quaternion_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[QUAT]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    elif packet_addr == gyro_bias_start_addr:
                        if len(packet) == 19:
                            logging.info("[GYRO_1_BIAS]: broadcast packet found!")
                            yield self.decode_gyro_bias_broadcast(packet)
                            received_packets += 1
                        else:
                            logging.error(f"[GYRO_1_BIAS]: invalid packet length, got {len(packet)}, packet: {packet}!")
                    else:
                        logging.error(f"[BROADCAST ERROR]: packet with addr {packet_addr}, reg: {start_reg.name} found "
                                      f"of length: {len(packet)} bytes, "
                                      f"no decoding is implemented for this!! Packet: {packet}")

    def decode_all_raw_broadcast(self, packet) -> UM7AllRawPacket:
        payload = packet[5:-2]
        g_x, g_y, g_z, g_time = struct.unpack('>hhh2xf', payload[0:12])
        a_x, a_y, a_z, a_time = struct.unpack('>hhh2xf', payload[12:24])
        m_x, m_y, m_z, m_time = struct.unpack('>hhh2xf',   payload[24:36])
        T, T_t = struct.unpack('>ff', payload[36:44])
        return UM7AllRawPacket(gyro_raw_x=g_x, gyro_raw_y=g_y, gyro_raw_z=g_z, gyro_raw_time=g_time,
                               accel_raw_x=a_x, accel_raw_y=a_y, accel_raw_z=a_z, accel_raw_time=a_time,
                               mag_raw_x=m_x, mag_raw_y=m_y, mag_raw_z=m_z, mag_raw_time=m_time,
                               temperature=T, temperature_time=T_t)

    def decode_all_proc_broadcast(self, packet) -> UM7AllProcPacket:
        payload = packet[5:-2]
        g_x, g_y, g_z, g_time = struct.unpack('>ffff', payload[0:16])
        a_x, a_y, a_z, a_time = struct.unpack('>ffff', payload[16:32])
        m_x, m_y, m_z, m_time = struct.unpack('>ffff', payload[32:48])
        return UM7AllProcPacket(gyro_proc_x=g_x, gyro_proc_y=g_y, gyro_proc_z=g_z, gyro_proc_time=g_time,
                                accel_proc_x=a_x, accel_proc_y=a_y, accel_proc_z=a_z, accel_proc_time=a_time,
                                mag_proc_x=m_x, mag_proc_y=m_y, mag_proc_z=m_z, mag_proc_time=m_time)

    def decode_euler_broadcast(self, packet) -> UM7EulerPacket:
        payload = packet[5:-2]
        roll, pitch, yaw = struct.unpack('>hhh2x', payload[0:8])
        roll_rate, pitch_rate, yaw_rate, time_stamp = struct.unpack('>hhh2xf', payload[8:20])
        return UM7EulerPacket(
            roll=roll/91.02222, pitch=pitch/91.02222, yaw=yaw/91.02222,
            roll_rate=roll_rate/91.02222, pitch_rate=pitch_rate/91.02222, yaw_rate=yaw_rate/91.02222,
            time_stamp=time_stamp
        )

    def decode_quaternion_broadcast(self, packet) -> UM7QuaternionPacket:
        payload = packet[5:-2]
        q_w, q_x, q_y, q_z, q_time = struct.unpack('>hhh2xf', payload[0:12])
        return UM7QuaternionPacket(
            q_w=q_w/29789.09091, q_x=q_x/29789.09091, q_y=q_y/29789.09091, q_z=q_z/29789.09091, q_time=q_time
        )

    def decode_raw_accel_broadcast(self, packet) -> UM7RawAccelPacket:
        payload = packet[5:-2]
        a_x, a_y, a_z, a_time = struct.unpack('>hhh2xf', payload[0:12])
        return UM7RawAccelPacket(accel_raw_x=a_x, accel_raw_y=a_y, accel_raw_z=a_z, accel_raw_time=a_time)

    def decode_raw_gyro_broadcast(self, packet) -> UM7RawGyroPacket:
        payload = packet[5:-2]
        g_x, g_y, g_z, g_time = struct.unpack('>hhh2xf', payload[0:12])
        return UM7RawGyroPacket(gyro_raw_x=g_x, gyro_raw_y=g_y, gyro_raw_z=g_z, gyro_raw_time=g_time)

    def decode_raw_mag_broadcast(self, packet) -> UM7RawMagPacket:
        payload = packet[5:-2]
        m_x, m_y, m_z, m_time = struct.unpack('>hhh2xf', payload[0:12])
        return UM7RawMagPacket(mag_raw_x=m_x, mag_raw_y=m_y, mag_raw_z=m_z, mag_raw_time=m_time)

    def decode_proc_accel_broadcast(self, packet) -> UM7ProcAccelPacket:
        payload = packet[5:-2]
        a_x, a_y, a_z, a_time = struct.unpack('>ffff', payload[0:16])
        return UM7ProcAccelPacket(accel_proc_x=a_x, accel_proc_y=a_y, accel_proc_z=a_z, accel_proc_time=a_time)

    def decode_proc_gyro_broadcast(self, packet) -> UM7ProcGyroPacket:
        payload = packet[5:-2]
        g_x, g_y, g_z, g_time = struct.unpack('>ffff', payload[0:16])
        return UM7ProcGyroPacket(gyro_proc_x=g_x, gyro_proc_y=g_y, gyro_proc_z=g_z, gyro_proc_time=g_time)

    def decode_proc_mag_broadcast(self, packet) -> UM7ProcMagPacket:
        payload = packet[5:-2]
        m_x, m_y, m_z, m_time = struct.unpack('>ffff', payload[0:16])
        return UM7ProcMagPacket(mag_proc_x=m_x, mag_proc_y=m_y, mag_proc_z=m_z, mag_proc_time=m_time)

    def decode_gyro_bias_broadcast(self, packet) -> UM7GyroBiasPacket:
        payload = packet[5:-2]
        gyro_bias_x, gyro_bias_y, gyro_bias_z, = struct.unpack('>fff', payload[0:12])
        return UM7GyroBiasPacket(gyro_bias_x=gyro_bias_x, gyro_bias_y=gyro_bias_y, gyro_bias_z=gyro_bias_z)

    def decode_health_broadcast(self, packet) -> UM7HealthPacket:
        payload = packet[5:-2]
        health, = struct.unpack('>I', payload[0:4])
        return UM7HealthPacket(health=health)


if __name__ == '__main__':
    pass
    um7 = UM7Serial()
