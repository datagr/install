import os.path
import shutil
from . import util

def build(docker_file, tag = None):
    if tag is None:
        tag = os.path.basename(docker_file)
    util.cmd("docker build -f {} -t {} .".format(docker_file, tag), verbose=True)
    return tag



