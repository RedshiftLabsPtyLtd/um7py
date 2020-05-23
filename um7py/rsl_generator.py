#!/usr/bin/env python

# Author: Dr. Konstantin Selyunin
# License: MIT

import logging
import os
import os.path
import struct
import textwrap

from typing import Any, List, Tuple

from jinja2 import Environment, DictLoader

from rsl_xml_svd.rsl_svd_parser import Register, RslSvdParser


class RslGenerator(RslSvdParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def retrieve_payload_description(self, register: Register) -> str:
        payload_description = ''
        for field in register.fields:
            field_description = ""
            if field.bit_range[0] > field.bit_range[1]:
                field_description += f"[{field.bit_range[0]}:{field.bit_range[1]}]"
            else:
                field_description += f"[{field.bit_range[0]}]"
            indent_spaces = 8 - len(field_description)
            field_description += " " * indent_spaces + f": {field.name} -- {field.description}\n"
            payload_description += field_description
        return textwrap.indent(payload_description[:-1], ' ' * 4)

    @staticmethod
    def render_template_to_str(template_file: str, params_dict: dict):
        if not os.path.exists(template_file):
            raise FileNotFoundError("Template file to render is not found!")

        with open(template_file, 'r') as fd:
            jinja_template = fd.read()

        template = Environment(loader=DictLoader({'jinja_template': jinja_template}))
        return template.get_template('jinja_template').render(params_dict)

    def retrieve_return_description(self, register: Register):
        return_description = ' '
        for idx, field in enumerate(register.fields):
            return_description += f"{field.name} as {field.data_type}; "
        return return_description

    def get_struct_fmt_for_data_type(self, el: str):
        data_types_mapping = {
            'uint8_t':  'B',
            'int8_t':   'b',
            'uint16_t': 'H',
            'int16_t':  'h',
            'uint32_t': 'I',
            'int32_t':  'i',
            'uint64_t': 'Q',
            'int64_t':  'q',
            'float':    'f',
            'double':   'd',
            'string':   's'
        }
        return data_types_mapping.get(el)

    def get_struct_fmt_for_register(self, register: Register):
        struct_fmt = '>'  # big-endian
        dword_bit_sets = set(range(31, 24, -1)), set(range(23, 16, -1)), set(range(15, 8, -1)), set(range(7, 0, -1))
        packed_fields = [field for field in register.fields if field.data_type != 'bitField']
        fields = [None] * 4
        for idx, bits in enumerate(dword_bit_sets):
            for field in packed_fields:
                if bits.issubset(set(range(*field.bit_range, -1))):
                    fields[idx] = field.name
        # remove duplicates in field names while keeping the MSB..LSB order
        fields_name_uniq = []
        field_name_seen = set()
        for field in fields:
            if field is None:
                fields_name_uniq.append(field)
            elif field in field_name_seen:
                continue
            else:
                fields_name_uniq.append(field)
                field_name_seen.add(field)
        # iterate over uniq field names of packed (i.e. non-bitField data)
        for field_name in fields_name_uniq:
            if field_name is None:
                struct_fmt += 'x'
            else:
                field = register.find_field_by(name=field_name)
                struct_fmt += self.get_struct_fmt_for_data_type(field.data_type)
        return struct_fmt

    def interpret_bitfields(self, register: Register) -> Tuple[str, str]:
        generated_code = "payload_uint32, = struct.unpack('>I', payload[0:4])\n"
        generated_code += f"reg = self.svd_parser.find_register_by(name='{register.name}')\n"
        return_vars = []
        register_bitfields = [field for field in register.fields if field.data_type == 'bitField']
        for field in register_bitfields:
            generated_code += f"# find value for {field.name} bit field\n"
            bit_mask = 2 ** (field.bit_range[0] - field.bit_range[1] + 1) - 1
            field_value_var = f"{field.name.lower()}_val"
            generated_code += f"{field_value_var} = (payload_uint32 >> {field.bit_range[1]}) & 0x{bit_mask:04X}\n"
            return_var = f"{field.name.lower()}_enum"
            return_vars.append(return_var)
            generated_code += f"{return_var} = reg.find_field_by(name='{field.name}')"\
                              f".find_enum_entry_by(value={field_value_var})\n"
        return ", ".join(return_vars), generated_code

    def interpret_packed_data(self, register: Register) -> Tuple[str, str]:
        return_vars = tuple(field.name.lower() for field in register.fields if field.data_type != 'bitField')
        generated_code = ", ".join(return_vars) + \
                         f" = struct.unpack('{self.get_struct_fmt_for_register(register)}', payload[0:4])"
        return ", ".join(return_vars), generated_code

    def interpret_string_data(self, register: Register) -> Tuple[str, str]:
        return_vars = tuple(field.name.lower() for field in register.fields)
        if len(return_vars) > 1:
            raise NotImplementedError(f"Multiple string fields in register is not supported! Check {register.name}!")
        field_name = return_vars[0]
        generated_code = f"{field_name} = struct.unpack('>4s', payload[0:4])[0].decode('utf-8')"
        return f'{field_name}', generated_code

    def interpret_payload(self, register: Register) -> Tuple[str, str]:
        field_type = [el.data_type for el in register.fields]
        if all([el == 'bitField' for el in field_type]):
            # all fields are bitfields
            return self.interpret_bitfields(register)
        elif not any([el == 'bitField' for el in field_type]) and not any([el == 'string' for el in field_type]):
            # all fields are of: uint8, int8, uint16, int16, uint32, int32, or float, i.e. in struct.fmt
            return self.interpret_packed_data(register)
        elif all([el == 'string' for el in field_type]):
            # fields are strings
            return self.interpret_string_data(register)
        elif any([el == 'bitField' for el in field_type]) and not any([el == 'string' for el in field_type]):
            # fields are combination of "bitFields" with types: uint8, int8, uint16, int16, uint32, int32, or float
            return_vars_packed, generated_code_packed = self.interpret_packed_data(register)
            return_vars_bitfields, generated_code_bitfields = self.interpret_bitfields(register)
            return return_vars_packed + ', ' + return_vars_bitfields, \
                   generated_code_packed + '\n' + generated_code_bitfields
        else:
            return '', f'Not Implemented for {register}'

    def create_getter_property(self, register: Register, is_hidden: bool = False) -> str:
        return_vars, generated_code = self.interpret_payload(register)
        params_dict = {
            'register_name': register.name.lower(),
            'comment_short': textwrap.indent(register.description, ' ' * 4),
            'payload_structure_description': self.retrieve_payload_description(register),
            'return_field_description': self.retrieve_return_description(register),
            'register_addr': register.address,
            'hidden': is_hidden,
            'interpreted_receive_fields': textwrap.indent(generated_code, ' ' * 8),
            'return_values': return_vars
        }
        getter_template_file = os.path.join(os.path.dirname(__file__), 'templates/getter_template.jinja2')
        getter = RslGenerator.render_template_to_str(getter_template_file, params_dict)
        return getter

    def create_default_getter(self, register: Register) -> str:
        params_dict = {
            'register_name': register.name.lower()
        }
        no_getter_template_file = os.path.join(os.path.dirname(__file__), 'templates/no_getter_template.jinja2')
        no_getter = RslGenerator.render_template_to_str(no_getter_template_file, params_dict)
        return no_getter

    def create_setter_property(self, register: Register, is_hidden: bool = False):
        params_dict = {
            'register_name': register.name.lower(),
            'register_addr': register.address,
            'hidden': is_hidden
        }
        setter_template_file = os.path.join(os.path.dirname(__file__), 'templates/setter_template.jinja2')
        setter = RslGenerator.render_template_to_str(setter_template_file, params_dict)
        return setter

    def generate_props_for_register(self, register: Register, is_hidden: bool = False):
        if register.access == 'read-only':
            return self.create_getter_property(register, is_hidden)
        elif register.access == 'write-only':
            return self.create_default_getter(register) + \
                   self.create_setter_property(register, is_hidden)
        elif register.access == 'read-write':
            return self.create_getter_property(register, is_hidden) + \
                   self.create_setter_property(register, is_hidden)
        else:
            raise NotImplementedError(f"register access can only be: `read-write`, `read-only`, `write-only`, " 
                                      f"but you provide: {register.access}")

    def generate_props_for_main_register_map(self):
        generated_main_register_map = ''
        for reg in self.regs:
            generated_main_register_map += self.generate_props_for_register(reg, is_hidden=False)
        return generated_main_register_map

    def generate_props_for_hidden_registers(self):
        generated_hidden_register_map = ''
        for reg in self.hidden_regs:
            generated_hidden_register_map += self.generate_props_for_register(reg, is_hidden=True)
        return generated_hidden_register_map


if __name__ == '__main__':
    pass

