#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# Date: 2 March 2020
# Version: v0.1
# License: MIT

import struct

from abc import abstractmethod, ABC
from typing import Union, Tuple


class RslException(Exception):
    """
    RSL Exception class:
    passing an error message when raising the Exception
    """
    def __init__(self, msg):
        self.msg = msg


class RslComm(ABC):

    @abstractmethod
    def connect(self, *args, **kwargs):
        pass

    @abstractmethod
    def read_register(self, reg_addr: int) -> bytes:
        pass

    @abstractmethod
    def write_register(self, reg_addr: int, reg_value: Union[int, bytes, float]):
        pass
