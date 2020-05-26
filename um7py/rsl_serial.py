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
from typing import Tuple, List, Dict, Any, Union

from um7py.rsl_comm import RslComm, RslException


class RslSerial(RslComm):
    def __init__(self, **kwargs):
        self.device_file = kwargs.get('device')
        self.device_dict = None
        self.port = serial.Serial()
        self.port_name = None
        self.port_config = None
        self.buffer = bytes()
        self.buffer_size = 512
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

    def find_response(self, reg_addr: int, hidden: bool = False) -> Tuple[bool, bytes]:
        while len(self.buffer) > 0:
            packet, self.buffer = self.find_packet(self.buffer)
            if len(packet) < 4:
                return False, bytes()
            logging.debug(f"{packet}")
            logging.debug(f"addr: {packet[4]}")
            packet_type = packet[3]
            is_packet_hidden = bool((packet_type >> 1) & 0x01)
            response_addr = packet[4]
            if response_addr == reg_addr and hidden == is_packet_hidden:
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
        ok, sensor_reply = self.find_response(reg_addr, hidden)
        if ok:
            logging.debug(f"packet: {sensor_reply}")
            self.check_packet(sensor_reply)
            ok, payload = self.get_payload(sensor_reply)
            return ok, payload
        else:
            while monotonic() - t < 0.15:
                # try to send <-> receive packets for a pre-defined time out time
                self.send_recv(packet_to_send)
                ok, sensor_reply = self.find_response(reg_addr, hidden)
                if ok:
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

    def decode_raw_gyro_packet(self, packet):
        payload = packet[5:-2]
        assert len(payload) == 44, "Invalid payload length for raw gyro packet"
        gyro_raw_x, gyro_raw_y, gyro_raw_z = struct.unpack('>hhh2x', payload[0:8])
        gyro_raw_time = struct.unpack('>f', payload[8:12])[0]
        accel_raw_x, accel_raw_y, accel_raw_z = struct.unpack('>hhh2x', payload[12:20])
        accel_raw_time = struct.unpack('>f', payload[20:24])[0]
        mag_raw_x, mag_raw_y, mag_raw_z = struct.unpack('>hhh2x', payload[24:32])
        mag_raw_time = struct.unpack('>f', payload[32:36])[0]
        temperature, temperature_time = struct.unpack('>ff', payload[36:44])
        return gyro_raw_x, gyro_raw_y, gyro_raw_z, \
               gyro_raw_time, \
               accel_raw_x, accel_raw_y, accel_raw_z, \
               accel_raw_time, \
               mag_raw_x, mag_raw_y, mag_raw_z, \
               mag_raw_time, \
               temperature, temperature_time

    def decode_proc_gyro_packet(self, packet):
        payload = packet[5:-2]
        assert len(payload) == 48, f"Invalid payload length for proc gyro packet, got {len(payload)},\n{payload}"
        gyro_proc_x, gyro_proc_y, gyro_proc_z = struct.unpack('>fff', payload[0:12])
        gyro_proc_time = struct.unpack('>f', payload[12:16])[0]
        acc_proc_x, acc_proc_y, acc_proc_z = struct.unpack('>fff', payload[16:28])
        acc_proc_time = struct.unpack('>f', payload[28:32])[0]
        mag_proc_x, mag_proc_y, mag_proc_z = struct.unpack('>fff', payload[32:44])
        mag_proc_time = struct.unpack('>f', payload[44:48])[0]
        return gyro_proc_x, gyro_proc_y, gyro_proc_z,\
               gyro_proc_time,\
               acc_proc_x, acc_proc_y, acc_proc_z,\
               acc_proc_time,\
               mag_proc_x, mag_proc_y, mag_proc_z,\
               mag_proc_time

    def decode_gyro_bias_packet(self, packet):
        payload = packet[5:-2]
        assert len(payload) == 12, f"Invalid payload length for gyro bias packet, got {len(payload)}"
        gyro_bias_x, gyro_bias_y, gyro_bias_z = struct.unpack('>fff', payload)
        return gyro_bias_x, gyro_bias_y, gyro_bias_z


