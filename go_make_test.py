import re
import sys
import pathlib
import subprocess
from configparser import ConfigParser

CONFIG_PATH: pathlib.Path = pathlib.Path(__file__).parent.parent.parent / "setup.cfg"

STD_OUT_LOG = pathlib.Path("./zdevelop/tests/_reports/test_stdout.txt")
STD_ERR_LOG = pathlib.Path("./zdevelop/tests/_reports/test_stderr.txt")
FULL_LOG = pathlib.Path("./zdevelop/tests/_reports/test_full.txt")
COVERAGE_LOG = pathlib.Path("./zdevelop/tests/_reports/coverage.out")
TEST_REPORT = pathlib.Path("./zdevelop/tests/_reports/test_results.html")
COVERAGE_REPORT = pathlib.Path("./zdevelop/tests/_reports/coverage/index.html")

COVERAGE_REGEX = re.compile(r"total:\s+\(statements\)\s+(\d+\.\d)%")


def load_cfg() -> ConfigParser:
    """
    loads library config file
    :return: loaded `ConfigParser` object
    """
    config = ConfigParser()
    config.read(CONFIG_PATH)
    return config


def run_test():
    config = load_cfg()
    coverage_required = config.getfloat("testing", "coverage_required") * 100
    test_package = config.get("testing", "test_package", fallback="./...")
    exclude_string = config.get("testing", "exclude", fallback="")
    exclude_list = [e for e in exclude_string.split("\n") if e]
    race_detection = config.getboolean("testing", "race_detection", fallback=True)
    multi_process = config.getboolean("testing", "multi_process", fallback=True)
    timeout = config.getint("testing", "timeout", fallback=60)

    # Get the list of packages we want to cover
    list_process = subprocess.Popen(
        ["go", "list", test_package], stdout=subprocess.PIPE, universal_newlines=True
    )

    grep_command = ["grep", "-v"]
    for this_exclude in exclude_list:
        grep_command += ["-e", this_exclude]

    sys.stdout.write(f"grep: {' '.join(grep_command)}\n")
    grep_process = subprocess.Popen(
        grep_command,
        stdin=list_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    list_process.stdout.close()
    packages_str, _ = grep_process.communicate()
    packages = packages_str.split("\n")
    if not packages:
        packages = ["./..."]

    sys.stdout.write(f"COVERAGE REQUIRED: {coverage_required}\n")

    # Set up the command
    command = [
        "go",
        "test",
        "-v",
        "-failfast",
        f"-timeout={timeout}s",
    ]

    # Add the race flag if we are using it.
    if race_detection:
        command.append("-race")

    # Add th flag to restrict the number of simultaneous tests to 1.
    if not multi_process:
        command.extend(("-p", "1"))

    # Finish building the command.
    command.extend(
        [
            "-covermode=atomic",
            f"-coverprofile={COVERAGE_LOG}",
            f"-coverpkg={','.join(packages)}",
        ]
    )

    command = command + ["./..."]

    sys.stdout.write(f"command: {' '.join(command)}\n")

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    stdout, stderr = proc.communicate()

    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    STD_OUT_LOG.write_text(stdout)
    STD_ERR_LOG.write_text(stderr)
    FULL_LOG.write_text(stdout + stderr)

    if proc.returncode != 0:
        sys.exit(proc.returncode)

    # Use the cov command to generate the total coverage
    command = [
        "go",
        "tool",
        "cover",
        "--func",
        COVERAGE_LOG,
    ]

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    stdout, stderr = proc.communicate()

    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    with STD_OUT_LOG.open("a") as f:
        f.write(stdout)
    with STD_ERR_LOG.open("a") as f:
        f.write(stderr)

    if proc.returncode != 0:
        sys.exit(proc.returncode)

    # Get the last coverage tally in the result
    coverage_str = [x for x in COVERAGE_REGEX.finditer(stdout)][-1].group(1)
    coverage = float(coverage_str)

    if coverage < coverage_required:
        sys.stderr.write(
            f"Coverage {coverage} is less than required {coverage_required}\n"
        )
        sys.exit(1)
    else:
        sys.stderr.write(
            f"Coverage {coverage}% passes requirement of {coverage_required}%\n"
        )


if __name__ == "__main__":
    run_test()
