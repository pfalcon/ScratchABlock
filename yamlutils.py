import yaml

import utils


def set_representer(dumper, data):
    return dumper.represent_list(sorted(list(data), key=utils.natural_sort_key))


yaml.add_representer(set, set_representer)
