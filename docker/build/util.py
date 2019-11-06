import os
import tempfile
import shutil
import sys
import shlex
import subprocess
from contextlib import contextmanager

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


def make_tarfile(flow_prefix):
    tar_file = "{}.tar.gz".format(flow_prefix)
    cmd("tar -czf {} {}".format(tar_file, flow_prefix))
    shutil.copy(tar_file, "/tmp")
    return os.path.join("/tmp/", tar_file)

