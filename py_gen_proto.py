import pathlib
import os
import sys
import subprocess
from typing import List


def main():
    generate_python_source()


def generate_python_source():
    proto_files = find_proto_files()
    run_protoc_command(proto_files)
    fix_generated_files()


def find_proto_files() -> List[str]:
    proto_file_list: List[str] = list()

    directory = pathlib.Path(os.getcwd())
    for proto_path in directory.rglob("./astral_proto/**/*.proto"):
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
        "python3",
        "-m",
        "grpc_tools.protoc",
        "-I.",
        "--python_out=./astral_grpc",
        "--python_grpc_out=./astral_grpc",
        "--mypy_out=./astral_grpc",
    ]
    command.extend(protoc_files)
    return command


def fix_import_paths(python_file: pathlib.Path, pyi: bool):
    file_text = python_file.read_text()
    file_text = file_text.replace("from astral_proto", "from astral_grpc.astral_proto",)
    file_text = file_text.replace(
        "import astral_proto", "import astral_grpc.astral_proto",
    )

    if not pyi:
        file_text = file_text.replace("[astral_proto", "[astral_grpc.astral_proto",)

    file_text = file_text.replace(" astral_proto.", " astral_grpc.astral_proto.",)
    python_file.write_text(file_text)


def fix_generated_files():
    for python_file in pathlib.Path("./astral_grpc/astral_proto").rglob("./**/*.py"):
        fix_import_paths(python_file, pyi=False)

    for python_file in pathlib.Path("./astral_grpc/astral_proto").rglob("./**/*.pyi"):
        fix_import_paths(python_file, pyi=True)


if __name__ == "__main__":
    main()
