#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Substitute all 'my' references to the python standard 'self' in a source tree
#

import os
import re
import tempfile
import shutil
import argparse


def traverse_dir(src_path=None):
    pattern = r'^.*\.py$'
    py_file_re = re.compile(pattern)

    for dir_name, subdir_list, file_list in os.walk(src_path):
        if re.search(r'.*\.git\/.*', dir_name):
            continue
        for file_name in file_list:
            if py_file_re.search(file_name):
                full_file_name = os.path.join(dir_name,file_name)
                print('-- %s' % full_file_name)
                my_to_self(full_file_name)


def my_to_self(file_name):
    my_self_re_1 = re.compile(r'([\s+,\(,\[,{,#,\*\*,%,\',/,+,-,=,:])my([\,,\.,:,\s+,\),\[,\])])')
    my_self_re_2 = re.compile(r'(\s*)my$')
    my_self_re_3 = re.compile(r'(")my(.)')
    my_self_re_4 = re.compile(r'()my2()')

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(file_name) as open_file:

            for line in open_file:
                line = my_self_re_1.sub(r'\1self\2', line)
                line = my_self_re_2.sub(r'\1self', line)
                line = my_self_re_3.sub(r'\1self\2', line)
                line = my_self_re_4.sub(r'\1self2\2', line)
                tmp_file.write(line)

        # Copy preserving file attributes to tmp_file
        shutil.copystat(file_name, tmp_file.name)
        # Overwrite the original file
        shutil.move(tmp_file.name, file_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Substitute all 'my' references to the python standard 'self'")
    parser.add_argument('src_path', help='Path for source code to be modified')
    args = parser.parse_args()

    traverse_dir(src_path=args.src_path)

