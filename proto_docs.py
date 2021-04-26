import sys
import pathlib
import subprocess
import os
from configparser import ConfigParser
from typing import List

ROOT_DIR = pathlib.Path(__file__).parent.parent.parent
CONFIG_PATH: pathlib.Path = ROOT_DIR / "setup.cfg"


def load_cfg() -> ConfigParser:
    """
    loads library config file
    :return: loaded `ConfigParser` object
    """
    config = ConfigParser()
    config.read(CONFIG_PATH)
    return config


def expand_directories(config_paths: List[str]) -> List[str]:
    working_dir_str = os.getcwd()

    proto_paths: List[str] = list()
    for this_path_str in config_paths:
        this_path = pathlib.Path(this_path_str).absolute()
        if not this_path.exists():
            raise FileExistsError(f"{this_path_str} does not exist")

        if this_path.is_dir():
            for this_proto_path in this_path.rglob("./**/*.proto"):
                this_proto_str = str(this_proto_path)
                this_proto_str = this_proto_str.replace(working_dir_str, ".")
                proto_paths.append(this_proto_str)
        else:
            proto_paths.append(this_path_str)

    return proto_paths


def make_proto_html() -> None:
    config = load_cfg()
    proto_files_string = config.get("docs.proto", "paths")
    config_paths = [f for f in proto_files_string.split("\n") if f]

    proto_files = expand_directories(config_paths)

    command = [
        "protoc",
        "--doc_out=./zdocs/source/_static",
        "--doc_opt=html,proto.html",
    ]
    command.extend(proto_files)

    proc = subprocess.Popen(
        command,
        cwd=str(ROOT_DIR),
    )

    _, _ = proc.communicate()
    sys.exit(proc.returncode)


if __name__ == "__main__":
    make_proto_html()
