import tempfile
import subprocess
import shlex
import yaml
from contextlib import contextmanager
import os


@contextmanager
def pushd(path):
    cwd = os.getcwd()
    os.chdir(path)

    yield

    os.chdir(cwd)


def cmd(cmd_string):
    subprocess.check_output( shlex.split(cmd_string) )


def git_clone(url, name):
    cmd("git clone {} {}".format(url, name))

def git_fetch(remote):
    cmd("git fetch {}".format(remote))

def git_checkout(git_ref):
    cmd("git checkout {}".format(git_ref))

def cmake(cmake_flags):
    cmake_cmdline = "cmake .. {}".format( " ".join(["-D{}={}".format(x[0], x[1]) for x in cmake_flags]))
    cmd(cmake_cmdline)

def make(num_cpu):
    cmd("make -j {}".format(num_cpu))

def make_install():
    cmd("make install")


class BuildObject(object):

    def make_cmake_flags(self, install_prefix):
        flags = [("CMAKE_INSTALL_PREFIX", install_prefix),
                 ("CMAKE_PREFIX_PATH", install_prefix),
                 ("BUILD_TESTING", "OFF"),
                 ("BUILD_SHARED_LIBS", "OFF")]

        for flag,value in self.cmake_flags:
            flags.append((flag, value))


    def __init__(self, config):
        self.name = config["name"]
        self.repo = config["repo"]
        self.git_ref = config["git_ref"]
        if "cmake_flags" in config:
            self.cmake_flags = config["cmake_flags"]
        else:
            self.cmake_flags = {}


    def build(self, install_prefix):
        with pushd(self.name):
            if not os.path.isdir("build"):
                os.mkdir("build")
            with pushd("build"):
                cmake(self.make_cmake_flags(install_prefix))
                make(8)
                make_install()


class BuildBoost(object):

    def __init__(self, config):
        self.version = config["version"]
        self.url = config["url"].format(self.version.replace("_", "."), self.version)
        self.libraries = config["libraries"]
        self.name = "boost_{}".format(self.version)


    def update_source(self):
        if not os.path.isdir(self.name):
            cmd("wget {}".format(self.url))
            cmd("tar -xvzf {}.tar.gz".format(self.name))

    def build(self, install_prefix):
        with pushd(self.name):
            cmd("./bootstrap.sh --prefix={}  --with-libraries={}".format(install_prefix, ",".join(self.libraries)))
            cmd("./b2 install link=static")



class BuildConfig(object):
    def __init__(self, config_file):
        config_data = yaml.safe_load( open(config_file) )
        self.src_list = [ BuildObject(src) for src in config_data["src"]]
        self.install_prefix = config_data["install_prefix"]
        self.boost = BuildBoost(config_data["boost"])



class Builder(object):

    def __init__(self, work_dir, config):
        if os.path.isdir(work_dir):
            os.chdir(work_dir)
        else:
            raise IOError("The work directory: {} does not exist".format(work_dir))
        self.config = config


    def update_source(self):
        self.config.boost.update_source()
        for src in self.config.src_list:
            if not os.path.isdir(src.name):
                git_clone(src.repo, src.name)

            with pushd(src.name):
                git_fetch("origin")
                git_checkout(src.git_ref)


    def build(self):
        self.config.boost.build(self.config.install_prefix)
        for src in self.config.src_list:
            src.build(self.config.install_prefix)

