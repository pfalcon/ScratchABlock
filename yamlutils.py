import yaml

import core


def set_representer(dumper, data):
    return dumper.represent_list(sorted(list(data), key=core.natural_sort_key))


yaml.add_representer(set, set_representer)
