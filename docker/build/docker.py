import json
import os.path
import shutil
from . import util

def build(docker_file, tag = None):
    if tag is None:
        tag = os.path.basename(docker_file)
    util.cmd("docker build -f {} -t {} .".format(docker_file, tag), verbose=True)
    return tag


def extract_files(base_image, file_list, target_path):
    code_cwd = os.path.abspath( os.path.dirname(__file__) )
    extract_script = os.path.join(code_cwd, "extract_files.py")
    if not os.path.isdir(target_path):
        os.makedirs(target_path)

    with util.pushd("/tmp/extract"):
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
        build("extract")
        util.cmd("docker run -v {}:/install extract".format(target_path), verbose = True)



def find_layer(fetch_id, cmd_string):
    # Export the content of the docker image to a tar file and unpack that
    # file. The tar file will unpack to a list of new tar files, one for each layer.
    util.cmd("docker save {} -o {}.tar".format(fetch_id, fetch_id))
    util.cmd("tar -xvf {}.tar".format(fetch_id), verbose=True)

    for path in os.listdir(os.getcwd()):
        if not os.path.isdir(path):
            continue

        json_file = os.path.join(path, "json")
        metadata = json.load(open(json_file))
        build_cmd = metadata["container_config"]["Cmd"]
        if build_cmd:
            for arg in build_cmd:
                if cmd_string in arg:
                    return path


def prefix_usr(arg):
    return arg.startswith("usr")


def installed_files(base_id, cmd_string, filter_func):
    layer_id = find_layer(base_id, cmd_string)
    tar_output = util.cmd("tar -xvf {}/layer.tar".format(layer_id))
    return filter( filter_func, tar_output.split())

