#!/usr/bin/env python
import json
import subprocess
import shlex
import sys
from contextlib import contextmanager
import tempfile
import os
import shutil

@contextmanager
def pushd(path):
    cwd = os.getcwd()
    if not os.path.isdir(path):
        os.makedirs(path)
    os.chdir(path)

    yield

    os.chdir(cwd)


@contextmanager
def tmpd():
    cwd = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)

    yield

    os.chdir(cwd)
    try:
        shutil.rmtree(tmp)
    except OSError:
        sys.stderr.write("Failed to clean up: {} - must run as root to clean\n".format(tmp))


def cmd(cmd_string, verbose = False):
    if verbose:
        print(cmd_string)

    stdout = subprocess.check_output( shlex.split(cmd_string))

    if verbose:
        print(stdout)
    return stdout


def docker_build(docker_file, tag = None):
    if tag is None:
        tag = os.path.basename(docker_file)
    cmd("docker build -f {} -t {} .".format(docker_file, tag), verbose=True)
    return tag


def find_layer(cmd_string):
    for path in os.listdir(os.getcwd()):
        if not os.path.isdir(path):
            continue

        json_file = os.path.join(path, "json")
        metadata = json.load(open(json_file))
        cmd = metadata["container_config"]["Cmd"]
        if cmd:
            for arg in cmd:
                if cmd_string in arg:
                    return path



def installed_files(layer_id, prefix):
    tar_output = cmd("tar -xvf {}/layer.tar".format(layer_id))
    return filter( lambda x: x.startswith(prefix), tar_output.split())


def extract_files(base_image, extract_script, file_list, target_path):
    if not os.path.isdir(target_path):
        os.makedirs(target_path)

    with pushd("/tmp/extract"):
        shutil.copy(extract_script, os.path.join(os.getcwd(), "extract_files.py"))
        with open("file_list.txt", "w") as fh:
            for fn in file_list:
                fh.write(fn + "\n")

        with open("extract","w") as f:
            f.write("""
FROM {}
COPY extract_files.py extract_files.py
COPY file_list.txt file_list.txt
ENTRYPOINT ["./extract_files.py", "file_list.txt", "{}"]
""".format(base_image, "/install"))
        docker_build("extract")
        cmd("docker run -v {}:/install extract".format(target_path), verbose = True)



def make_tarfile(flow_prefix):
    tar_file = "{}.tar.gz".format(flow_prefix)
    cmd("tar -czf {} {}".format(tar_file, flow_prefix))
    shutil.copy(tar_file, "/tmp")
    return os.path.join("/tmp/", tar_file)


def make_enable(flow_prefix):
    with open("{}/enable".format(flow_prefix), "w") as f:
        f.write("""
#!/bin/bash

root=
export LD_LIBRARY_PATH=${{root}}/{}/usr/lib64:$LD_LIBRARY_PATH
export PATH=${{root}}/{}/usr/bin:$PATH
""".format(flow_prefix, flow_prefix))


def copy_data(src_path, target_path):
    shutil.copytree(src_path, target_path)



script_path = os.path.abspath( os.path.dirname(__file__) )
flow_version = "2019.04"
os_image = "centos-7"

fetch_file = os.path.join(script_path, "dockerfiles/{}/fetch".format(os_image))
install_file = os.path.join(script_path, "dockerfiles/{}/install".format(os_image))
extract_script = os.path.join(script_path, "extract_files.py")
data_path = os.path.join(script_path, "testdata")

fetch_id = docker_build(fetch_file)

with tmpd():
    cmd("docker save {} -o {}.tar".format(fetch_id, fetch_id))
    cmd("tar -xvf {}.tar".format(fetch_id), verbose=True)
    layer_id = find_layer("opm-simulators-")
    files = installed_files(layer_id, "usr")
    with tmpd():
        flow_prefix = "flow-{}".format(flow_version)
        extract_files(fetch_id, extract_script, files, os.path.join( os.getcwd(), flow_prefix))
        make_enable(flow_prefix)
        copy_data(data_path, "{}/testdata".format(flow_prefix))
        tar_file = make_tarfile(flow_prefix)
        print("Tar file: {} created".format(tar_file))
        with pushd(flow_prefix):
            docker_build(install_file, "{}-{}".format(os_image, flow_version))
