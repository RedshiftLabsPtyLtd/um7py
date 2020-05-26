#!/usr/bin/env python3
# Author: Dr. Konstantin Selyunin
# Date: 26 May 2020
# License: MIT

from shutil import copy
import os
import os.path
import stat


def serve_autodetect_script(target_dir='./'):
    """
    Copies UM7 autodetect script in target directory
    :param target_dir: directory to copy autodetect script to
    :return: 0 -- execution successful
    """
    autodetect_script = 'um7_autodetect.py'
    src_path = os.path.dirname(os.path.abspath(__file__))
    autodetect_script_orig = os.path.join(src_path, autodetect_script)
    autodetect_script_copied = os.path.join(target_dir, autodetect_script)
    copy(autodetect_script_orig, autodetect_script_copied)
    # make copied file executable
    st = os.stat(autodetect_script_copied)
    os.chmod(autodetect_script_copied, st.st_mode | stat.S_IEXEC)
