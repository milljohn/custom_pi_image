import logging
import os
from logging import debug, info, warning, error
import json
import sys

logging_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
logging.basicConfig(format='%(asctime)s-[%(process)d]-%(levelname)s-%(message)s', level=logging_level)


def read_config(path: str):
    """

    Load configuration from json file.

    :param path: json formatted file path
    :return: None
    """

    if not os.path.exists(path):
        error(f'{path} does not exist')
        sys.exit(-1)

    try:
        with open(path, 'r') as f:
            # TODO: validate json formatting
            return json.load(f)
    except Exception as e:
        error(f'Error reading {path}: {e}')
def main():
    config = read_config('../configs.json')
    # print(config)
    print(config.keys())
    for val in config:
        print(config[val])


if __name__ == '__main__':
    main()
