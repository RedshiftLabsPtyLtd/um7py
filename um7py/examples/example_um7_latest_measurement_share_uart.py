#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# License: MIT
# Date: 28 March 2021
import json
import logging
from pathlib import Path
import sys

from um7py.um7_serial import UM7Serial
from um7py.um7_broadcast_packets import UM7AllProcPacket, UM7AllRawPacket
from multiprocessing import shared_memory, Process, Lock
from time import sleep, time


BUFFER_SIZE = 1000
raw_data_shm = shared_memory.SharedMemory(create=True, size=BUFFER_SIZE)
proc_data_shm = shared_memory.SharedMemory(create=True, size=BUFFER_SIZE)
raw_lock = Lock()
proc_lock = Lock()


def sensor_read_process(raw_shm: shared_memory.SharedMemory, proc_shm: shared_memory.SharedMemory, r_lock: Lock, p_lock: Lock):
    script_dir = Path(__file__).parent
    device_file = script_dir.parent.joinpath("um7_A500CNP8.json")
    assert device_file.exists(), f"Device file with connection info: {device_file} does not exist!"
    um7 = UM7Serial(device=str(device_file))

    for packet in um7.recv_broadcast(flush_buffer_on_start=False):
        packet_bytes = bytes(json.dumps(packet.__dict__), encoding='utf-8')
        assert len(packet_bytes) <= BUFFER_SIZE, f"Packet cannot be serialized, increase `BUFFER` size at least up to {len(packet_bytes)}"
        if isinstance(packet, UM7AllRawPacket):
            r_lock.acquire()
            raw_shm.buf[:] = b' ' * BUFFER_SIZE
            raw_shm.buf[:len(packet_bytes)] = packet_bytes
            r_lock.release()
            # logging.warning(f"[SR][RAW] -> {packet}")
        elif isinstance(packet, UM7AllProcPacket):
            p_lock.acquire()
            proc_shm.buf[:] = b' ' * BUFFER_SIZE
            proc_shm.buf[:len(packet_bytes)] = packet_bytes
            p_lock.release()
            # logging.warning(f"[SR][PROC] -> {packet}")


def main_function():
    start_time = time()

    idx = 0
    while time() - start_time < 60:
        idx += 1
        if idx % 2 == 0:
            # imagine I need to process raw data now
            raw_lock.acquire()
            raw_meas_bytes: bytes = raw_data_shm.buf[:]
            raw_lock.release()
            raw_meas_str = str(raw_meas_bytes, encoding='utf-8')
            raw_meas_dict = json.loads(raw_meas_str)
            packet = UM7AllRawPacket(**raw_meas_dict)
            logging.warning(f"[MF][RAW]: {packet}")
            sleep(3.0)  # move motors, do some hard work
        else:
            # here I need ot handle proc data
            proc_lock.acquire()
            proc_meas_bytes: bytes = proc_data_shm.buf[:]
            proc_lock.release()
            proc_meas_str = str(proc_meas_bytes, encoding='utf-8')
            proc_meas_dict = json.loads(proc_meas_str)
            packet = UM7AllProcPacket(**proc_meas_dict)
            logging.warning(f"[MF][PROC]: {packet}")
            sleep(2.0)  # move motors, do some hard work


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='[%(asctime)s.%(msecs)03d]: %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(f'{Path(__file__).stem}.log', mode='w'),
            logging.StreamHandler(sys.stdout),
        ])
    sensor_read_proc = Process(target=sensor_read_process, args=(raw_data_shm, proc_data_shm, raw_lock, proc_lock,))
    sensor_read_proc.start()

    sleep(1)
    main_function()

    proc_data_shm.close()
    proc_data_shm.unlink()

    raw_data_shm.close()
    raw_data_shm.unlink()
