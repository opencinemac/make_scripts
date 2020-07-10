import pathlib


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
    fix_generated_files()
