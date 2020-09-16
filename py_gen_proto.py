import pathlib
import sys
import subprocess
import dataclasses
import configparser
from typing import List


CONFIG_PATH: pathlib.Path = pathlib.Path("./setup.cfg").absolute()


@dataclasses.dataclass
class Options:
    """Dataclass used to hold the relevant options from our config file."""

    proto_root_dir: pathlib.Path
    """Root path to our protobuf folder."""
    output_dir: pathlib.Path
    """Directory to output the generated files."""
    original_import: str
    """The original import path prefix in the generated python files."""
    new_import: str
    """The new import path prefix for the generated python files."""


def load_cfg() -> Options:
    """
    loads library config file
    :return: loaded `Options` object
    """
    config = configparser.ConfigParser()
    config.read(str(CONFIG_PATH))

    options = Options(
        proto_root_dir=pathlib.Path(config["proto"]["root_source_path"]),
        output_dir=pathlib.Path(config["proto"]["python_output_path"]),
        original_import=config["proto"]["python_import_original"],
        new_import=config["proto"]["python_import_replacement"],
    )

    return options


def main():
    options = load_cfg()
    generate_python_source(options)


def generate_python_source(options: Options):
    proto_files = find_proto_files(options)
    run_protoc_command(proto_files)
    fix_generated_files(options)


def find_proto_files(options: Options) -> List[str]:
    proto_file_list: List[str] = list()

    for proto_path in options.proto_root_dir.rglob("./**/*.proto"):
        path_str = str(proto_path)
        path_str = path_str.replace(str(options.proto_root_dir), ".")
        proto_file_list.append(path_str)

    return proto_file_list


def run_protoc_command(proto_files: List[str]) -> None:
    command = build_protoc_command(proto_files)

    proc = subprocess.Popen(command)
    _, _ = proc.communicate()
    if proc.returncode != 0:
        sys.exit(proc.returncode)


def build_protoc_command(protoc_files: List[str], options: Options) -> List[str]:
    command = [
        "python3",
        "-m",
        "grpc_tools.protoc",
        "-I.",
        f"--python_out={options.output_dir}",
        f"--python_grpc_out={options.output_dir}",
        f"--mypy_out={options.output_dir}",
    ]
    command.extend(protoc_files)
    return command


def fix_import_paths(python_file: pathlib.Path, pyi: bool, options: Options):
    file_text = python_file.read_text()
    file_text = file_text.replace(
        f"from {options.original_import}", f"from {options.new_import}",
    )
    file_text = file_text.replace(
        f"import {options.original_import}", f"import {options.new_import}",
    )

    if not pyi:
        file_text = file_text.replace(
            f"[{options.original_import}", f"[{options.new_import}",
        )

    file_text = file_text.replace(
        f" {options.original_import}.", f" {options.new_import}.",
    )
    python_file.write_text(file_text)


def fix_generated_files(options: Options):
    for python_file in pathlib.Path(options.output_dir).rglob("./**/*.py"):
        fix_import_paths(python_file, pyi=False, options=options)

    for python_file in pathlib.Path(options.output_dir).rglob("./**/*.pyi"):
        fix_import_paths(python_file, pyi=True, options=options)


if __name__ == "__main__":
    main()
