
import json
from codecs import open


def write_dict(d, filepath, encoding='utf-8'):
    """
    Write a dictionary to a JSON file.

    :param dict d: Dictionary to write
    :param str filepath: Path to file
    :param str encoding: File encoding to use
    """
    with open(filepath, mode='w', encoding=encoding) as f:
        f.write(json.dumps(d))


def read_dict(filepath, encoding='utf-8'):
    """
    Read a dictonary from a JSON file.

    :param str filepath: Path to file
    :param str encoding: File encoding to use
    :returns: The dictionary
    :rtype: dict
    """
    with open(filepath, mode='r', encoding=encoding) as f:
        return json.loads(f.read())
