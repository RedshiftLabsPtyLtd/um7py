# Author: Dr. Konstantin Selyunin
# Date: 7 April 2020
# Version: v0.1
# License: MIT

import os
import os.path

from um7py.rsl_generator import RslGenerator
from textwrap import indent
from datetime import datetime


if __name__ == '__main__':
    script_folder = os.path.dirname(__file__)
    svd_file = os.path.join(script_folder, os.pardir, './um7py/rsl_xml_svd/um7.svd')
    rsl_svd_generator = RslGenerator(svd_file=svd_file)
    um7_main_registers = indent(rsl_svd_generator.generate_props_for_main_register_map(), ' ' * 4)
    um7_hidden_registers = indent(rsl_svd_generator.generate_props_for_hidden_registers(), ' ' * 4)

    today = datetime.now().strftime('%Y.%m.%d')
    params_dict = {
        'generated_code_for_main_register_map': um7_main_registers,
        'generated_code_for_hidden_register_map': um7_hidden_registers,
        'today': today
    }
    um7_template = os.path.join(os.path.dirname(__file__), 'templates/um7_template.jinja2')
    gen_code = RslGenerator.render_template_to_str(um7_template, params_dict)
    with open('um7_registers.py', 'w') as fd:
        fd.write(gen_code)

    reg_addr_enum_template = os.path.abspath('templates/python_reg_acces.jinja2')
    param_dict = {'version': 'v0.1',
                  'date': today,
                  'cregs': rsl_svd_generator.cregs,
                  'dregs': rsl_svd_generator.dregs,
                  'commands': rsl_svd_generator.commands}
    gen_code = RslGenerator.render_template_to_str(reg_addr_enum_template, param_dict)
    with open('um7_py_accessor.py', 'w') as fd:
        fd.write(gen_code)

