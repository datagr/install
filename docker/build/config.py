import yaml
import os.path

from .util import pushd

class Config(object):

    def __init__(self, fname):
        config_data = yaml.safe_load(open(fname))
        with pushd(os.path.dirname(fname)):
            self.base_file = os.path.abspath(config_data["dockerfile"]["base"])
            self.install_file = os.path.abspath(config_data["dockerfile"]["install"])
            self.enable_in = os.path.abspath(config_data["enable"])
            self.readme_in = os.path.abspath(config_data["README"])

        self.os_image = config_data["os_image"]
        self.mpi = config_data["mpi"]
        self.version = config_data["version"]

