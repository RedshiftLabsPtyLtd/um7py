#!/usr/bin/env python

# Author: Dr. Konstantin Selyunin
# License: MIT

import os
import os.path

from dataclasses import dataclass
from typing import Any, List, Tuple, Union
from xml.etree import ElementTree as ET


@dataclass
class EnumeratedValue:
    name: str
    description: str
    value: int

    def __repr__(self):
        return f"EnumeratedValue(name={self.name}, value={self.value})"


@dataclass
class Field:
    name: str
    description: str
    bit_range: Tuple[int]
    data_type: str
    access: str
    enumerated_values: Tuple[EnumeratedValue] = tuple()
    scale_factor: float = 1.0
    bias_factor: float = 0.0

    def __repr__(self):
        return f"Field(name={self.name}, "\
               f"bit_range={self.bit_range}, data_type={self.data_type}, "\
               f"access={self.access}, enumerated_values={self.enumerated_values})"

    def find_enum_entry_by(self, **kw) -> EnumeratedValue:
        (prop, value), = kw.items()
        if len(kw) != 1 or prop not in ['name', 'value']:
            raise NotImplementedError(f"One pair is supported, with key either `name` or `value`, but given: {kw}!")
        found_enum = next(filter(lambda x: getattr(x, prop) == value, self.enumerated_values), None)
        return found_enum

    def get_c_type(self) -> str:
        c_type_mapping = {
            'bitField' : 'uint32_t',
            'uint8_t'  : 'uint8_t',
            'int8_t'   : 'int8_t',
            'uint16_t' : 'uint16_t',
            'int16_t'  : 'int16_t',
            'uint32_t' : 'uint32_t',
            'int32_t'  : 'int32_t',
            'uint64_t' : 'uint64_t',
            'int64_t'  : 'int64_t',
            'float'    : 'float',
            'double'   : 'double',
            'string'   : 'char'
        }
        return c_type_mapping[self.data_type]


@dataclass
class Register:
    name: str
    description: str
    access: str
    address: int
    fields: List[Field]

    def __repr__(self):
        return f"Register(name={self.name}, address={self.address}, access={self.access}, fields={self.fields})"

    def find_field_by(self, name: str = '', bit_position: int = -1) -> Union[Field, None]:
        if name != '':
            return next(filter(lambda x: x.name == name, self.fields), None)
        elif bit_position != -1:
            return next(
                filter(lambda x: bit_position in set(range(x.bit_range[1], x.bit_range[0] + 1)), self.fields), None)
        else:
            return None

    def get_fields_and_gaps(self) -> List:
        register_bits = range(0, 32)
        field_in_bit_position = []
        for bit in register_bits:
            found_field = self.find_field_by(bit_position=bit)
            if found_field is None:
                field_in_bit_position.append(Field(name=None, description='', bit_range=(0,), data_type='', access=''))
            else:
                field_in_bit_position.append(found_field)
        fields_and_gaps = []
        for el in field_in_bit_position:
            if len(fields_and_gaps) == 0 or (el.name not in fields_and_gaps[-1].keys()):
                fields_and_gaps.append({el.name: 1})
            elif el.name in fields_and_gaps[-1].keys():
                fields_and_gaps[-1][el.name] += 1
        return fields_and_gaps


class RslSvdParser:

    def __init__(self, *args, **kwargs):
        self.svd_xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'um7.svd')) if not kwargs.get('svd_file') else kwargs.get('svd_file')
        self.svd_xml_root = RslSvdParser.parse_svd_file(self.svd_xml_file)
        self.svd_regs = RslSvdParser.find_main_register_xml_root_in_svd(self.svd_xml_root)
        self.hidden_regs_xml = RslSvdParser.find_hidden_register_xml_root_in_svd(self.svd_xml_root)
        self.svd_cregs = self.find_cregs_in_svd()
        self.svd_dregs = self.get_dregs_from_svd()
        self.svd_commands = self.get_commands_from_svd()
        self.cregs = self.get_cregs_objects()
        self.dregs = self.get_dreg_objects()
        self.commands = self.get_commands_objects()
        self.hidden_regs = self.get_hidden_objects()
        self.regs = self.cregs + self.dregs + self.commands

    @staticmethod
    def parse_svd_file(file_to_parse: str):
        if not os.path.exists(file_to_parse):
            raise FileNotFoundError(f"Non-existing SVD file provided, check if ``{file_to_parse}`` exists!")
        return ET.parse(file_to_parse).getroot()

    @staticmethod
    def find_main_register_xml_root_in_svd(parsed_xml_tree_root: ET.Element) -> ET.Element:
        main_register_map_peripheral = parsed_xml_tree_root.find('.//peripheral/[name="UM7_MAIN_REGISTER_MAP"]')
        return main_register_map_peripheral.findall('.//register')

    @staticmethod
    def find_hidden_register_xml_root_in_svd(parsed_xml_tree_root: ET.Element) -> ET.Element:
        hidden_register_map_peripheral = parsed_xml_tree_root.find('.//peripheral/[name="UM7_HIDDEN_REGISTER_MAP"]')
        return hidden_register_map_peripheral.findall('.//register')

    def find_cregs_in_svd(self) -> Tuple[Any, ...]:
        return tuple(el for el in self.svd_regs if 'CREG' in el.find('./name').text)

    def get_dregs_from_svd(self) -> Tuple[Any, ...]:
        return tuple(el for el in self.svd_regs if 'DREG' in el.find('./name').text)

    def get_commands_from_svd(self) -> Tuple[Any, ...]:
        return tuple(el for el in self.svd_regs if int(el.find('./address').text, 16) >= 0xAA)

    def get_cregs_objects(self) -> Tuple[Register]:
        return tuple(self.extract_register_fields(el) for el in self.svd_cregs)

    def get_dreg_objects(self) -> Tuple[Register]:
        return tuple(self.extract_register_fields(el) for el in self.svd_dregs)

    def get_commands_objects(self) -> Tuple[Register]:
        return tuple(self.extract_register_fields(el) for el in self.svd_commands)

    def get_hidden_objects(self) -> Tuple[Register]:
        return tuple(self.extract_register_fields(el) for el in self.hidden_regs_xml)

    @staticmethod
    def find_by(registers: Tuple[Register], **kw) -> Union[None, Register]:
        (prop, value), = kw.items()
        if len(kw) > 1 or prop not in ['name', 'address']:
            raise NotImplementedError(f"One pair is supported, with key either `name` or `address`, but given: {kw}!")
        found_register = next(filter(lambda x: getattr(x, prop) == value, registers), None)
        return found_register

    def find_register_by(self, **kw):
        return RslSvdParser.find_by(self.regs, **kw)

    def find_hidden_register_by(self, **kw):
        return RslSvdParser.find_by(self.hidden_regs, **kw)

    @staticmethod
    def get_enumerated_value(enum_value: ET.Element) -> EnumeratedValue:
        name = enum_value.find('.//name').text
        description = enum_value.find('.//description').text
        value = int(enum_value.find('.//value').text)
        return EnumeratedValue(name=name, description=description, value=value)

    def get_enumerated_values(self, enum_values: ET.Element) -> Tuple[EnumeratedValue]:
        if enum_values:
            return tuple(self.get_enumerated_value(child) for child in enum_values)

    def extract_field_info(self, field: ET.Element) -> Field:
        name = field.find('.//name').text
        description = field.find('.//description').text
        bit_range_str = field.find('.//bitRange').text
        bit_range = tuple(int(el) for el in bit_range_str.strip('[]').split(':'))
        access = field.find('.//access').text
        data_type = field.find('.//dataType').text
        enumerated_values = self.get_enumerated_values(field.find('.//enumeratedValues'))
        scale_factor_xml = field.find('.//conversionScaleFactor')
        scale_factor = '' if scale_factor_xml is None else scale_factor_xml.text
        bias_factor_xml = field.find('.//conversionBiasFactor')
        bias_factor = '' if bias_factor_xml is None else bias_factor_xml.text
        return Field(name=name,
                     description=description,
                     bit_range=bit_range,
                     data_type=data_type,
                     access=access,
                     enumerated_values=enumerated_values,
                     scale_factor=scale_factor,
                     bias_factor=bias_factor)

    def extract_register_fields(self, reg_desc: ET.Element) -> Register:
        reg_name = reg_desc.find('.//name').text
        reg_access = reg_desc.find('.//access').text
        description = reg_desc.find('.//description').text
        address = int(reg_desc.find('.//address').text, 16)
        fields = reg_desc.findall('.//field')
        field_info = [self.extract_field_info(field) for field in fields]
        return Register(name=reg_name,
                        access=reg_access,
                        description=description,
                        address=address,
                        fields=field_info)


if __name__ == '__main__':
    pass

