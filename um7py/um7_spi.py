#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# Date: 12 June 2020
# Version: v0.1
# License: MIT

from um7py.rsl_spi import RslSpiUsbIss, RslSpiLinuxPort
from um7py.um7_registers import UM7Registers


class UM7SpiLinuxPort(RslSpiLinuxPort, UM7Registers):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class UM7SpiUsbIss(RslSpiUsbIss, UM7Registers):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == '__main__':
    um7_spi_iss = UM7SpiUsbIss()
    print(f"creg_com_settings             : {um7_spi_iss.creg_com_settings}")
    print(f"creg_com_rates1               : {um7_spi_iss.creg_com_rates1}")
    print(f"creg_com_rates2               : {um7_spi_iss.creg_com_rates2}")
    print(f"creg_com_rates3               : {um7_spi_iss.creg_com_rates3}")
    print(f"creg_com_rates4               : {um7_spi_iss.creg_com_rates4}")
    print(f"creg_com_rates5               : {um7_spi_iss.creg_com_rates5}")
    print(f"creg_com_rates6               : {um7_spi_iss.creg_com_rates6}")
    print(f"creg_com_rates7               : {um7_spi_iss.creg_com_rates7}")
