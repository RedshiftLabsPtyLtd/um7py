# UM7 Python 3 Driver

[![PyPI version](https://badge.fury.io/py/um7py.svg)](https://badge.fury.io/py/um7py)
![test and package](https://github.com/RedshiftLabsPtyLtd/um7py/workflows/test%20and%20package/badge.svg)

**TL;DR:** *"Swiss army knife"* for using 
the [`UM7`](https://redshiftlabs.com.au/product/um7-orientation-sensor/) 
orientation sensor with Python 3 (Python 3.6+).

`UM7` comes with the 
[_"Serial Software Interface"_](https://redshiftlabs.com.au/support-services/serial-interface-software/)
for handling / communicating with the sensor, which is currently available for Windows only.

The `python` driver provided here is designed to keep you up and running 
on different platforms (Linux, Windows, Mac).
If you have the `UM7` board and want to use it on Linux (e.g. Ubuntu, Debian, Raspbian, Yocto, Suse, etc.),
Windows or Mac, this repo provides driver code to send / receive individual packets
and receive broadcasts, as well example code how to create a sensor communication object.

In particular, the driver has the following capabilities: 

* read / write single `UM7` registers over UART;

* receive broadcast data from the `UM7` sensor over UART;

* register map and interpretation of the sensor registers.

## Repo structure

To get started, you need to know that communicating with the UM7 over
the UART is coded in [`um7_serial.py`](./um7py/um7_serial.py) file, 
where the `UM7Serial` class is defined. 
Information about UM7 registers comes to [`um7_serial.py`](./um7py/um7_serial.py)
from the [`um7_registers.py`](./um7py/um7_registers.py) file, where 
the accessing to the UM7 registers are stored.
Since it is possible to access the UM7 register map over UART and SPI,
the register data (e.g. addresses, fields, and their meaning) is stored in a separate file.
In the [`examples`](./um7py/examples) folder we store the examples how to communicate with the 
sensor. 

The UM7 register description is stored in the SVD file [`um7.svd`](./um7py/rsl_xml_svd/um7.svd)
and is parsed by the [`rsl_svd_parser.py`](./um7py/rsl_xml_svd/rsl_svd_parser.py).
The parser extracts the information from the XML file and keeps it as python data classes.

Below we outline the repo structure:   

* [`um7py`](./um7py): top-level python package;
* [`um7py/examples`](./um7py/examples): package with example code for receiving broadcast / reading / writing UM7 registers;
* [`um7py/rsl_xml_svd`](./um7py/rsl_xml_svd): package that stores UM7 registers data in SVD (or **S**ystem **V**iew **D**escription) format and parsing code;
* [`um7py/rsl_xml_svd/test`](./um7py/rsl_xml_svd/test): [`pytest`](https://docs.pytest.org/en/latest/) tests for SVD parsing;
* [`um7py/rsl_xml_svd/RSL-SVD.xsd`](./um7py/rsl_xml_svd/RSL-SVD.xsd): RedShiftLabs SVD [XML Schema](https://www.w3schools.com/xml/xml_schema.asp) based on [CMSIS5 SVD Schema](https://github.com/ARM-software/CMSIS);
* [`um7py/rsl_xml_svd/rsl_svd_parser.py`](./um7py/rsl_xml_svd/rsl_svd_parser.py): parsing code for [um7.svd](./um7py/rsl_xml_svd/um7.svd) into dataclasses;
* [`um7py/rsl_xml_svd/um7.svd`](./um7py/rsl_xml_svd/um7.svd): the UM7 SVD file, which stores register description in xml (in particular SVD format);
* [`um7py/templates`](./um7py/templates): [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) templates used for code generation part;
* [`um7py/test`](./um7py/test): [pytest](https://docs.pytest.org/en/latest/) tests for code generation part;
* [`um7py/rsl_generate_um7.py`](./um7py/rsl_generate_um7.py): invoke code generation and save generated results;
* [`um7py/rsl_generator.py`](./um7py/rsl_generator.py): code generation for [`um7_registers.py`](./um7py/um7_registers.py) from the SVD file;
* [`um7py/serve_um7_autodetect.py`](./um7py/serve_um7_autodetect.py): copies the [`um7_autodetect.py`](./um7py/um7_autodetect.py) script to the desired location;
* [`um7py/um7_autodetect.py`](./um7py/um7_autodetect.py): UM7 script for saving configuration for connection to the [USB Expansion Board](https://redshiftlabs.com.au/product/usb-expansion-board/);  
* [`um7py/um7_broadcast_packets.py`](./um7py/um7_broadcast_packets.py): [dataclasses](https://docs.python.org/3/library/dataclasses.html) for UM7 broadcast messages;
* [`um7py/um7_registers.py`](./um7py/um7_registers.py): UM7 register description file;
* [`um7py/um7_serial.py`](./um7py/um7_serial.py): UM7 UART driver;

## HW Prerequisites

UM7 provides serial (UART) and SPI interfaces, hence the two main ways to access the sensor data
are UART (serial) or SPI. The differences in short: UART provides broadcast functionality, i.e.
when packets can transmitted by the board with a specified frequency (transmission frequencies are set up in 
configuration registers), and it is possible to issue sensor commands (i.e. accessing command registers).
SPI access the sensor register on demand (i.e. no broadcast functionality), and only
configuration and data registers can be accessed. Accessing commands is only supported
over UART.

### Serial connection (UART)

When using UM7 over serial, it is possible to connect to the target system (i.e. user's target):

* to the serial port directly (e.g. when serial pins are wired out as on the 
[Raspberry PI](https://www.raspberrypi.org/), 
[NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit), 
or other board computers with GPIO and UART pins wired out);

* to the USB port using the  [USB Expansion Board](https://redshiftlabs.com.au/product/usb-expansion-board/),
which performs USB to serial conversion.

### SPI connection

When using the UM7 over SPI, there are also a couple of possibilities:

* to the SPI pins directly (e.g. Raspberry PI, NVIDIA Jetson Nano), i.e.
the pins are wired to the [SoC](https://en.wikipedia.org/wiki/System_on_a_chip) directly;

* to the USB port using USB to SPI converter, e.g. [USB-ISS](https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm).

The difference between the two, that in the first case SoC pins support the SPI
directly (on the hardware level, which also mirrors in the OS level), then the OS is likely to have the SPI device
driver built-in (e.g. Raspberry PI). In the second case, using external converter (e.g. USB-ISS),
the device will be shown as a so-called [cdc_acm](https://www.keil.com/pack/doc/mw/USB/html/group__usbh__cdcacm_functions.html) (communication device class),
and low-level SPI communication will be done by the converter, yet to the OS the 
converter will be shown as Abstract Control Model (ACM) USB Device.

## Installation

```sh
pip install um7py
```

## Python dependencies

**TL;DR:** install 
(i) `pyserial`, 
(ii) `pyudev` (for Linux),
(iii) `dataclasses` (included in standard library since `python3.7`, needs to be installed for `3.6`).

If you want to use SPI: if using on Linux and use SPI bus directly, install `spidev`,
otherwise if using USB-ISS install `usb_iss` python package.

## Quick start

Create `UM7` serial communication object, UM7 connected to a port `/dev/ttyUSB0`,
and read the firmware version:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
print(f"um7 firmware revision: {um7_serial.get_fw_revision}")
```

Reading **all types** of broadcast packets from `UM7`, 1000 packets in total:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
for packet in um7_serial.recv_broadcast(num_packets=1000):
    print(f"packet: {packet}")
```

Reading the **raw sensor data** broadcast packets from `UM7`, not limiting number of packets:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
for packet in um7_serial.recv_all_raw_broadcast():
    print(f"packet: {packet}")
```

Reading 100 **processed sensor data** broadcast packets from `UM7`:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
for packet in um7_serial.recv_all_proc_broadcast(num_packets=100):
    print(f"packet: {packet}")
```

Reading the **Euler angles** broadcast packets from `UM7`:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
for packet in um7_serial.recv_euler_broadcast():
    print(f"packet: {packet}")
```

Reading the `CREG_COM_SETTINGS` configuration register from `UM7`:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
print(f"received value: {um7_serial.creg_com_settings}")
```

Writing 40 (changing `ALL_RAW_RATE` to 40 Hz) to the `CREG_COM_RATES2` register:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
um7_serial.creg_com_rates2 = 40
```

## Slow start

Take a look at the available [examples](./um7py/examples).

In order to use the `python` driver functionality one first needs to 
create a communication object (in our case `UM7Serial` or `UM7SPI`).

The construction of the UART communication object can be done 
either by specifying a `port_name` directly (e.g. `/dev/ttyS0`), or
by specifying the `device` file that stores *USB2Serial* config
(e.g. `um7_A500CNP8.json`). The `device` argument shall 
only be used, when UM7 is connected via the 
[USB Expansion Board](https://redshiftlabs.com.au/product/usb-expansion-board/),
the `device` stores properties of the expansion board. Why?
The issue to keep in mind that when the sensor is re-plugged,
it might appear to the OS as different serial connection,
i.e. when first plugged in the OS detects the device as
`/dev/ttyS0`, then after re-plugging exactly the same 
sensor might appear by different port name, e.g. `/dev/ttyS1`, which 
means the user code needs to be changed.
If using the `device`, we store properties of the
[USB Expansion Board](https://redshiftlabs.com.au/product/usb-expansion-board/)
in a JSON file (e.g. converter chip ID) 
and search connection which match with the properties, and 
in this case connecting to the sensor, even if is shown as a 
different serial connection by the OS.

So the communication object can either be created with specifying the `port_name`:

```python
from um7py import UM7Serial
um7_serial = UM7Serial(port_name='/dev/ttyUSB0')
```

Or with specifying the `device`:

```python
from um7py import UM7Serial
um7 = UM7Serial(device='um7_A500CNP8.json')
```

The two options are exclusive, i.e. specifying both `port_name` and `device` will not work.

Accessing to the individual registers is done via python 
[properties](https://docs.python.org/3/library/functions.html#property).
Properties for register names are all lower-case, split by `_`.

For example, reading the `CREG_COM_RATES1`:

```python
from um7py import UM7Serial
um7 = UM7Serial(device='um7_A500CNP8.json')
um7.creg_com_rates1
```

Note, that reading single register is quite a slow operation,
since one first constructs and sends a packet, and then parses 
output for response. 
Reading single registers is not recommended for reading sensor data,
since it might happen, that data from different sensor registers come from different measurements.
We strongly advice to use broadcast messages for reading sensor and fusion data.

## UM7 Data Packets

`UM7` sends different types of broadcast messages over the UART.
These messages are e.g. HEALTH packet (i.e. the `DREG_HEALTH` register),
raw sensor data (raw gyro, accelerometer, and magnetometer, and temperature),
processed sensor data (processed gyro, accelerometer, and magnetometer),
Euler angles, quaternions.

These data packets are stored in the repo as 
[dataclasses](https://docs.python.org/3/library/dataclasses.html)
in the file [um7_broadcast_packets.py](./um7py/um7_broadcast_packets.py).
Note, that only payload stored in the dataclasses, and all the 
checks (e.g. checksum, data length) is done during broadcast reception.

For example, the raw data broadcast message has the following payload:

```python
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
```

## Acknowledgement

We are so grateful for the open source community for creating
open source UM7 driver versions and sharing it with a world!
We are inspired by your work, and at the same time 
want to improve:
provide UART and SPI communication, in detail documentation 
and explanations to facilitate the start for new users.

The acknowledgments go to:

* [Daniel Kurek](https://github.com/dank93) and his
[um7](https://github.com/dank93/um7) repository,
for implementing the first driver for interfacing with UM7;
 
* [Till Busch](https://github.com/buxit) and his [um7](https://github.com/buxit/um7) 
fork of Daniel's Kurek repo, for extending on the Daniel's work and
adding new functionality.


## Maintainer

[Dr. Konstantin Selyunin](http://selyunin.com/), 
for suggestions / questions / comments 
please contact selyunin [dot] k [dot] v [at] gmail [dot] com.
