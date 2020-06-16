#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# Date: 12 June 2020
# Version: v0.3
# License: MIT

import logging
import os.path
import struct

from time import sleep
from typing import List, Union, Tuple

from um7py.um7_serial import RslException


class SpiCommunication:
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def connect(self, *args, **kwargs):
        pass

    def xfer(self, msg):
        raise NotImplemented("This method should be implemented in child classes!")

    def spi_xfer(self, msg):
        # self.ssn_pin.state = False
        sleep(0.05)
        response = self.xfer(msg)
        logging.warning(f'msg: {msg}\t\tresponse: {response}')
        sleep(0.01)
        # self.ssn_pin.state = True
        return response

    def read_register(self, reg_addr: int, **kw) -> Tuple[bool, bytes]:
        msg = [0x00, reg_addr] + [0x00] * 4
        response = self.spi_xfer(msg)
        return True, bytes(response[2:])

    def write_register(self, reg_addr: int, reg_value: Union[int, bytes, float], **kw):
        if type(reg_value) == float:
            reg_value = struct.pack('>f', reg_value)
        elif type(reg_value) == bytes:
            reg_value = list(reg_value)
        elif type(reg_value) == int:
            reg_value = int.to_bytes(reg_value, length=4, byteorder='big', signed=False)
        msg = [0x01, reg_addr] + list(reg_value)
        self.spi_xfer(msg)
        return True

    def read_consecutive_registers(self, reg_addr: int, num_registers: int):
        msg = [0x00, reg_addr] + [0x00] * 4 * num_registers
        response = self.spi_xfer(msg)
        return True, bytes(response[2:])


class RslSpiLinuxPort(SpiCommunication):
    def __init__(self, *args, **kwargs):
        import spidev
        super().__init__(args, kwargs)
        self.bus = kwargs.get('bus') if kwargs.get('bus') is not None else 0
        self.device = kwargs.get('device') if kwargs.get('device') is not None else 0
        self.spi_device_path = f'/dev/spidev{self.bus}.{self.device}'
        if not os.path.exists(self.spi_device_path):
            raise RslException(f'SPI device not found: {self.spi_device_path}')
        self.spi = spidev.SpiDev()
        self.connect()

    def connect(self, *args, **kwargs):
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 500000

    def xfer(self, bytes_to_send: List[int]) -> List[int]:
        tx_bytes = bytes_to_send[:]
        self.spi.xfer(tx_bytes)
        return tx_bytes


class RslSpiUsbIss(SpiCommunication):
    def __init__(self, **kwargs):
        from usb_iss import UsbIss
        super().__init__(**kwargs)
        self.iss = UsbIss()
        self.port = kwargs.get('port') if kwargs.get('port') is not None else '/dev/ttyACM0'
        if not os.path.exists(self.port):
            raise RslException(f'SPI port not found: {self.port}: USB-ISS needs to connect to ACM'
                               f' port for SPI communication. The port does not exist, specify `port` argument!')
        self.connect()

    def connect(self, *args, **kwargs):
        self.iss.open(self.port)
        self.iss.setup_spi(clock_khz=500)

    def xfer(self, bytes_to_send: List[int]) -> List[int]:
        recv_bytes = self.iss.spi.transfer(bytes_to_send)
        return recv_bytes


if __name__ == '__main__':
    pass
