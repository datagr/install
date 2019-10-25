#!/usr/bin/env python
import json
import subprocess
import shlex
import sys
import tempfile
import os
import shutil
import yaml
from contextlib import contextmanager

# The purpose of this script is to generate a tar file distribution of
# opm/flow. The script is based on docker, and the functionality can be briefly
# summarized as follows:
#
#  1. Start with a plain docker image for e.g. Centos or Ubuntu, and then build
#     a new image by running the equivalent of "apt-get install opm".
#
#  2. On the newly created image we run the command "docker save" which will
#     extract the layers in the docker image, from this we can identify the
#     layer which actually installs flow, and then get a listing of all the
#     files in that layer - these are the files we are interested in.
#
#  3. To actually extract the interesting files from the docker image we need
#     to start a docker container which mounts an outside path and then run a
#     script inside the container which copies all the interesting files to the
#     externally visible path.
#
#     Observe that the script also creates a docker image which can be
#     installed, that is not actually used.
#
#  4. Finally the script creates a small README and a small enable script,
#     copies in two folders of testdata and packs everything in .tar.gz file.
#
# The behaviour of the script is goverened by a small config file, which is
# given as commandline argument. This config file should contain the path to
# dockerfiles and template files for the enable script and readme files.
# Currently the configurations are organized with one complete configuration in
# a directory by itself.



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


class Config(object):

    def __init__(self, fname):
        config_data = yaml.safe_load(open(fname))
        with pushd(os.path.dirname(fname)):
            self.fetch_file = os.path.abspath(config_data["dockerfile"]["fetch"])
            self.install_file = os.path.abspath(config_data["dockerfile"]["install"])
            self.enable_in = os.path.abspath(config_data["enable"])
            self.readme_in = os.path.abspath(config_data["README"])

        self.os_image = config_data["os_image"]
        self.mpi = config_data["mpi"]
        self.version = config_data["version"]


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


def make_enable(config, flow_prefix):
    template = open(config.enable_in).read()
    with open("{}/enable".format(flow_prefix), "w") as f:
        f.write(template.format(flow_prefix = flow_prefix))


def make_README(config, flow_prefix):
    template = open(config.readme_in).read()
    with open("{}/README".format(flow_prefix), "w") as f:
        f.write(template.format(version = config.version,
                                flow_prefix = flow_prefix))


def copy_data(src_path, target_path):
    shutil.copytree(src_path, target_path)


def print_msg(tar_file):
    msg = """
Push tar file to google storage:

    gsutil cp {0} gs://datagr-export

Make file public:

    gsutil acl ch -u AllUsers:R gs://datagr-export/{1}

URL:

    https://storage.googleapis.com/datagr-export/{1}
""".format(tar_file, os.path.basename(tar_file))
    print(msg)



script_path = os.path.abspath( os.path.dirname(__file__) )
config = Config(sys.argv[1])
if config.mpi:
    flow_version = "2019.04-mpi"
else:
    flow_version = "2019.04"

extract_script = os.path.join(script_path, "extract_files.py")
data_path = os.path.join(script_path, "testdata")

# Create the main docker image where opm/flow is installed.
fetch_id = docker_build(config.fetch_file)

with tmpd():
    # Export the content of the docker image to a tar file and unpack that
    # file. The tar file will unpack to a list of new tar files, one for each layer.
    cmd("docker save {} -o {}.tar".format(fetch_id, fetch_id))
    cmd("tar -xvf {}.tar".format(fetch_id), verbose=True)

    # Inspect the layer metadata and find the layer which has actually
    # installed opm/flow.
    layer_id = find_layer("opm-simulators-")

    # Make a list of all the files with prefix /usr from the layer where
    # opm/flow is installed
    files = installed_files(layer_id, "usr")
    with tmpd():
        flow_prefix = "flow-{}".format(flow_version)
        # Run a docker container with a script to pull out all the files in the
        # list created by installed_files().
        extract_files(fetch_id, extract_script, files, os.path.join( os.getcwd(), flow_prefix))

        make_enable(config, flow_prefix)
        make_README(config, flow_prefix)
        copy_data(data_path, "{}/testdata".format(flow_prefix))
        tar_file = make_tarfile(flow_prefix)
        print("Tar file: {} created".format(tar_file))
        with pushd(flow_prefix):
            docker_build(config.install_file, "{}-{}".format(config.os_image, flow_version))

print_msg(tar_file)

