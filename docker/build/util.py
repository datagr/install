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

