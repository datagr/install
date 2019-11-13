import yaml
import os.path

from .util import pushd

class Config(object):

    def __init__(self, fname):
        self.base_file = None
        self.install_file = None
        self.build_file = None
        self.build_script = None

        config_data = yaml.safe_load(open(fname))
        with pushd(os.path.dirname(fname)):
            dockerfiles = config_data["dockerfiles"]
            if "base" in dockerfiles:
                self.base_file = os.path.abspath(dockerfiles["base"])

            if "install" in dockerfiles:
                self.install_file = os.path.abspath(dockerfiles["install"])

            if "build" in dockerfiles:
                self.build_file = os.path.abspath(dockerfiles["build"])

            self.enable_in = os.path.abspath(config_data["enable"])
            self.readme_in = os.path.abspath(config_data["README"])

            if "build_script" in config_data:
                self.build_script = os.path.abspath(config_data["build_script"])

        self.os_image = config_data["os_image"]
        self.mpi = config_data["mpi"]
        self.version = config_data["version"]

