import logging
from logging import config as logconfig
from pkgutil import get_data
from os import chmod
from os.path import exists, expanduser
from yaml import safe_load

configuration_file = '~/.choirsupport.yml'
example_configuration_file = 'example-config.yml'


def ensure_configuration_file_exists():
    if not exists(expanduser(configuration_file)):
        print("No %s found; instantiating..." % configuration_file)
        with open(expanduser(configuration_file), 'wb') as f:
            example_cfg = get_data('choirsupport', example_configuration_file)
            if example_cfg is None:
                print("WARN: cannot find example-config.yml")
            else:
                f.write(example_cfg.replace(b"%HOME%", bytes(expanduser("~"), "utf-8")))
                f.flush()
                print("Make sure only user can read and write configuration file")
                chmod(path=expanduser(configuration_file), mode=0o700)


def init():
    ensure_configuration_file_exists()
    with open(expanduser(configuration_file), 'r') as stream:
        config = safe_load(stream)
        logconfig.dictConfig(config['logging'])
        log = logging.getLogger(__name__)
        log.info("Initialized logging")
        return config


def recursive_merge(d1: dict, d2: dict):
    result = d1.copy()
    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = recursive_merge(result[key], value)
        else:
            result[key] = value
    return result
