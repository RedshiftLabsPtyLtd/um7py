# UM7 Python 3 Driver

**TL;DR:** *"Swiss army knife"* for using 
the [`UM7`](https://redshiftlabs.com.au/product/um7-orientation-sensor/) board
with Python 3 (Python 3.6+).

`UM7` comes with the 
[_"Serial Software Interface"_](https://redshiftlabs.com.au/support-services/serial-interface-software/)
for handling / communicating with the sensor, which is currently available for Windows only.

The `python` driver provided here is designed to keep you up and running 
on different platforms (Linux, Windows, Mac).
If you have the `UM7` board and want to use it on Linux (e.g. Ubuntu, Debian, Raspbian, Yocto, Suse, etc.),
Windows or Mac, this repo provides driver code to send / receive individual packets
and broadcasts, as well example code how to create a sensor communication object.

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

When using UM7 over serial, it is possible to connect to the target system (i.e. user's target):

* to the serial port directly (e.g. when serial pins are wired out as on the Raspberry PI, NVIDIA Jetson Nano, or other 
board computers with GPIO and UART pins wired out);

* to the USB port using the  [USB Expansion Board](https://redshiftlabs.com.au/product/usb-expansion-board/),
which performs USB to serial conversion.

When using the UM7 over SPI, there are also a couple of possibilities:

* to the SPI pins directly (e.g. Raspberry PI, NVIDIA Jetson Nano), i.e.
the pins are wired to the [SoC](https://en.wikipedia.org/wiki/System_on_a_chip) directly;

* to the USB port using USB to SPI converter, e.g. [USB-ISS](https://www.robot-electronics.co.uk/htm/usb_iss_tech.htm).
 
## Installation

## Python dependencies

## Quick start

## Cautious start

## UM7 Data Packets

## Acknowledgement

We are so grateful for the open source community for creating
open source UM7 driver versions and sharing it with a world!
We are inspired by your work, and at the same time 
want to improve on that:
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
please contact .
