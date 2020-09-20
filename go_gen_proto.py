import pathlib
import os
import sys
import subprocess
import configparser
import dataclasses
from typing import List


CONFIG_PATH: pathlib.Path = pathlib.Path("./setup.cfg").absolute()


@dataclasses.dataclass
class Options:
    """Dataclass used to hold the relevant options from our config file."""

    proto_root_dir: pathlib.Path
    """Root path to our protobuf folder."""
    go_module_root: str
    """Root module to use for protoc-gen-go '--go_opt=module=' flag."""


def load_cfg() -> Options:
    """
    loads library config file
    :return: loaded `Options` object
    """
    config = configparser.ConfigParser()
    config.read(str(CONFIG_PATH))

    options = Options(
        proto_root_dir=pathlib.Path(config["proto"]["root_source_path"]),
        go_module_root=pathlib.Path(config["proto"]["root_go_package"])
    )

    return options


def main():
    """Run the script."""
    options = load_cfg()
    generate_golang_source(options)
    add_bson_tags()


def generate_golang_source(options: Options):
    """Generate the protocol buffers."""
    proto_files = find_proto_files(options)
    run_protoc_command(proto_files, options)


def find_proto_files(options: Options) -> List[str]:
    """Glob all the proto files in the root proto folder and return as list."""
    proto_file_list: List[str] = list()

    for proto_path in options.proto_root_dir.rglob("./**/*.proto"):
        print(proto_path)
        if "google" in str(proto_path):
            continue

        path_str = str(proto_path)
        path_str = path_str.replace(str(os.getcwd()), ".")
        proto_file_list.append(path_str)

    return proto_file_list


def run_protoc_command(proto_files: List[str], options: Options) -> None:
    """Run the protoc command and stream the output to std out."""
    command = build_protoc_command(proto_files, options)

    proc = subprocess.Popen(command)
    _, _ = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def build_protoc_command(protoc_files: List[str], options: Options) -> List[str]:
    """Put together the protoc command to buid."""

    command = [
        "protoc",
        "--go_out=plugins=grpc:.",
        f"--go_opt=module={options.go_module_root}",
    ]
    command.extend(protoc_files)
    return command


def add_bson_tags():
    """Add bson tags through protoc-go-inject-tag."""
    directory = pathlib.Path(os.getcwd())
    for source_code_file_path in directory.rglob("./**/*.pb.go"):
        run_tag_command(source_code_file_path)


def build_tag_command(source_code_file_path: pathlib.Path) -> List[str]:
    """Build the protoc-go-inject-tag command."""
    return [
        "protoc-go-inject-tag",
        f"-input={source_code_file_path}",
        "-XXX_skip=bson",
    ]


def run_tag_command(source_code_path: pathlib.Path) -> None:
    """Run the protoc-go-inject-tag  command and stream the output to stdout."""
    command = build_tag_command(source_code_path)
    proc = subprocess.Popen(command)

    _, _ = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
