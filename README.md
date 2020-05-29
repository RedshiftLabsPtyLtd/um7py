# UM7 Python 3 Driver

This is the UM7 Python 3 driver.

**TL;DR:** *"Swiss army knife"* for using 
the [UM7](https://redshiftlabs.com.au/product/um7-orientation-sensor/)
with Python 3 (Python 3.6+).

`UM7` comes with the 
[_"Serial Software Interface"_](https://redshiftlabs.com.au/support-services/serial-interface-software/)
for handling / communicating with the sensor, which is currently available for Windows only.

The `python` driver provided here is designed to keep you up and running 
quickly on different platforms (Linux, Windows, Mac).
If you have the `UM7` board and want to use it on Linux (e.g. Ubuntu, Debian, Yocto, Suse),
Windows or Mac, this repo provides driver code to send / receive individual packets
and broadcasts, as well example code how to create a sensor communication object.

In particular, the driver has the following capabilities: 

* read / write single `UM7` registers over UART;

* receive broadcast data from the `UM7` sensor over UART;

* register map and interpretation of the sensor registers.

