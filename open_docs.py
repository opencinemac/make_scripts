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

    doc_index = "./zdocs/build/html/index.html"

    command1 = [command_base, doc_index]

    subprocess.Popen(command1, stdout=sys.stdout, stderr=sys.stderr).communicate()
