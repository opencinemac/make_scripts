import sys
import pathlib
import configparser


def load_cfg(config_path: pathlib.Path) -> configparser.ConfigParser:
    """
    loads library config file
    :return: loaded `ConfigParser` object
    """
    config = configparser.ConfigParser()
    config.read(str(config_path))
    return config


def main():
    config = load_cfg(pathlib.Path("./setup.cfg").absolute())
    service_name = config.get("metadata", "name")

    sys.stdout.write(service_name)


if __name__ == "__main__":
    main()
