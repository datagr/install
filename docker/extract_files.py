#!/usr/bin/env python
import sys
import os
import os.path
import shutil
from contextlib import contextmanager


@contextmanager
def pushd(path):
    cwd = os.getcwd()
    os.chdir(path)

    yield

    os.chdir(cwd)

def load_arglist(argv_file):
    return open(argv_file).read().split()



arg_list = load_arglist(sys.argv[1])
target_prefix = sys.argv[2]
for arg in arg_list:
    src_arg = "/{}".format(arg)
    if os.path.isdir(src_arg):
        target_path = os.path.join(target_prefix, arg)
        if not os.path.isdir(target_path):
            os.makedirs(target_path)

    if os.path.isfile(src_arg):
        if not os.path.islink(src_arg):
            shutil.copy(src_arg, os.path.join(target_prefix, arg))
            print(src_arg)


for arg in arg_list:
    src_arg = "/{}".format(arg)
    if os.path.islink(src_arg):
        link_target = os.readlink(src_arg)
        link_name = os.path.basename(src_arg)
        path = os.path.dirname(os.path.join(target_prefix, arg))
        with pushd(path):
            print("{}:  {} -> {}".format(path, link_name, link_target))
            try:
                os.symlink(link_target, link_name)
            except:
                pass
