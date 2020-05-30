#!/usr/bin/env python

# Author: Dr. Konstantin Selyunin
# License: MIT

import argparse
import json
import sys

from argparse import RawTextHelpFormatter
from typing import Tuple, Dict


def um7_autodetect(file_name=None):
    """
    :param file_name: by default ID of sensor will be assigned
    :return: id file will be created in target directory
    """

    def um7_windows_autodetect(config_file_name=None) -> Tuple[bool, Dict]:
        json_config = {}
        from serial.tools import list_ports
        device_list = list_ports.comports()
        for device in device_list:
            # go through device list and stop on first FTDI device
            if device.manufacturer == "FTDI":
                # found something, add keys
                # device.device is the port name (COM4 for example)
                json_config['ID_VENDOR'] = device.manufacturer
                json_config['ID_SERIAL_SHORT'] = device.serial_number
                # don't know what the model should look like so were making it "pid:vid"
                json_config['ID_MODEL'] = '{0:04x}:{1:04x}'.format(device.vid, device.pid)
                if config_file_name is None:
                    config_file_name = f"um7_{json_config['ID_SERIAL_SHORT']}.json"
                with open(config_file_name, 'w') as fp:
                    json.dump(json_config, fp, indent=2)
                return True, json_config
        # none of the devices was FTDI
        return False, {}

    def um7_linux_autodetect(config_file_name=None):
        json_config = {}
        import pyudev
        context = pyudev.Context()
        udev_keys = ['ID_VENDOR', 'ID_SERIAL_SHORT', 'ID_MODEL']
        for device in context.list_devices(subsystem='tty'):
            if device.get('ID_VENDOR') == 'FTDI':
                for key in udev_keys:
                    json_config[key] = device.get(key)
                if config_file_name is None:
                    config_file_name = f"um7_{json_config['ID_SERIAL_SHORT']}.json"
                with open(config_file_name, 'w') as fp:
                    json.dump(json_config, fp, indent=2)
                return True, json_config
            else:
                return False, {}

    if sys.platform.startswith('win32'):
        return um7_windows_autodetect(file_name)
    else:
        return um7_linux_autodetect(file_name)


description = """\
Save parameters of the USB2Serial device to a file,
when UM7 is used with USB2Serial converter.
USB2Serial for UM7 uses FTDI chip, and has no specific
descriptor information to differentiate itself
from other FTDI devices (e.g. stepper motors or other
devices implementing USB2Serial connection).

In order to differentiate these devices, we
created this script, which searches for available
devices and stores information in a .json file.
\n
Follow the procedure below:
-------------------------------
\n
1. Disconnect all the USB2Serial-related devices;
2. Connect UM7 sensor;
3. Launch the script (optional -f flag specifies file name);
4. The file `um7_[serial_id].json` containing device
specific information appears on success.

This file will be used by UM7 drivers
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', '--file', type=str, help='')
    args = parser.parse_args(sys.argv[1:])
    ok, config = um7_autodetect(args.file)
    print(config)
    if not ok:
        print("FAILED to store ID of UM7! Check whether the sensor is connected!")
