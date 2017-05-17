from collections import OrderedDict

import yaml

import utils


def set_representer(dumper, data):
    return dumper.represent_list(sorted(list(data), key=utils.natural_sort_key))


yaml.add_representer(set, set_representer)


# Workaround pyyaml idiocy of forcibly sort dicts by key
class DictRenderWrapper:

    def __init__(self, d):
        self.d = d

    def __iter__(self):
        return iter(self.d.items())


def dict_representer(dumper, data):
    ordered = OrderedDict()
    if "label" in data:
        ordered["label"] = data["label"]
    ordered.update(sorted(data.items()))
    return dumper.represent_dict(DictRenderWrapper(ordered))

yaml.add_representer(dict, dict_representer)
