import platform
import subprocess
import sys

PLATFORM = platform.system()

if __name__ == "__main__":
    if PLATFORM == "Darwin":
        command_base = "open"
    elif PLATFORM == "Linux":
        command_base = (
            "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
        )
    else:
        command_base = (
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        )

    report1 = "./zdevelop/tests/_reports/coverage.html"
    report2 = "./zdevelop/tests/_reports/test_results.html"

    command1 = [command_base, report1]
    command2 = [command_base, report2]

    subprocess.Popen(command1, stdout=sys.stdout, stderr=sys.stderr).communicate()
    subprocess.Popen(command2, stdout=sys.stdout, stderr=sys.stderr).communicate()
