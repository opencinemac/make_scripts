import pathlib
import os
import sys
import subprocess
from typing import List


def main():
    generate_golang_source()
    add_bson_tags()


def generate_golang_source():
    proto_files = find_proto_files()
    run_protoc_command(proto_files)


def find_proto_files() -> List[str]:
    proto_file_list: List[str] = list()

    directory = pathlib.Path(os.getcwd())
    for proto_path in directory.rglob("./astral_proto/**/*.proto"):
        if "google" in str(proto_path):
            continue

        path_str = str(proto_path)
        path_str = path_str.replace(str(directory), ".")
        proto_file_list.append(path_str)

    return proto_file_list


def run_protoc_command(proto_files: List[str]) -> None:
    command = build_protoc_command(proto_files)

    proc = subprocess.Popen(command)
    _, _ = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def build_protoc_command(protoc_files: List[str]) -> List[str]:
    command = [
        "protoc",
        "--go_out=plugins=grpc:.",
        "--go_opt=module=github.com/illuscio-dev/astralGrpc-go",
    ]
    command.extend(protoc_files)
    return command


def add_bson_tags():
    directory = pathlib.Path(os.getcwd())
    for source_code_path in directory.rglob("./messages/**/*.pb.go"):
        run_tag_command(source_code_path)


def build_tag_command(source_code_path: pathlib.Path) -> List[str]:
    return [
        "protoc-go-inject-tag",
        f"-input={source_code_path}",
        "-XXX_skip=bson",
    ]


def run_tag_command(source_code_path: pathlib.Path) -> None:
    command = build_tag_command(source_code_path)
    proc = subprocess.Popen(command)

    _, _ = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
