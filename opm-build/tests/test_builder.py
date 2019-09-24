import unittest
import yaml
from contextlib import contextmanager
import tempfile
import os

from build import Builder, BuildConfig


@contextmanager
def tmpd():
    cwd = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)

    yield

    os.chdir(cwd)

def example_config():
    return """
install_prefix: /tmp/builder-install

boost:
    version: "1_66_0"
    url: https://dl.bintray.com/boostorg/release/{}/source/boost_{}.tar.gz
    libraries:
    - date_time
    - system
    - filesystem
    - regex
    - test

src:
- name: trilinos
  git_ref: master
  repo: https://github.com/trilinos/Trilinos.git
  cmake_flags:
    Trilinos_ENABLE_Zoltan: ON

- name: dune-common
  git_ref: master
  repo: https://gitlab.dune-project.org/core/dune-common.git

- name: dune-grid
  git_ref: master
  repo: https://gitlab.dune-project.org/core/dune-grid.git

- name: dune-istl
  git_ref: master
  repo: https://gitlab.dune-project.org/core/dune-istl.git

- name: dune-geometry
  git_ref: master
  repo: https://gitlab.dune-project.org/core/dune-geometry.git

- name: dune-localfunctions
  git_ref: master
  repo: https://gitlab.dune-project.org/core/dune-localfunctions.git

- name: dune-fem
  git_ref: master
  repo: https://gitlab.dune-project.org/dune-fem/dune-fem.git

- git_ref: master
  name: libecl
  repo: https://github.com/equinor/libecl

- git_ref: master
  name: opm-common
  repo: https://github.com/OPM/opm-common

- git_ref: master
  name: opm-material
  repo: https://github.com/OPM/opm-material

- git_ref: master
  name: opm-grid
  repo: https://github.com/OPM/opm-grid

- git_ref: master
  name: opm-models
  repo: https://github.com/OPM/opm-models

- git_ref: master
  name: opm-simulators
  repo: https://github.com/OPM/opm-simulators
"""




class BuilderTest(unittest.TestCase):

    def setUp(self):
        pass

    def config_error(self, config, exc):
        with tmpd():
            with open("config", "w") as f:
                yaml.dump(config, f)

            with self.assertRaises(exc):
                bc = BuildConfig("config")

    def test_config(self):

        with self.assertRaises(IOError):
            bc = BuildConfig( "/does/not/exist")

        with tmpd():
            with open("config", "w") as f:
                f.write(example_config())

            work_dir = tempfile.mkdtemp()
            work_dir = "/tmp/builder-work"
            config = BuildConfig("config")
            builder = Builder(work_dir, config)
            builder.update_source()
            builder.build()


if __name__ == "__main__":
    unittest.main()
