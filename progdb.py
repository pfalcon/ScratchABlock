#
# This module deals with various "program databases" as required
# for analysis passes. Among them: function database (funcdb.yaml),
# databases of structures, etc.
#
import os.path

import yaml
import yamlutils

import core


FUNC_DB = {}
FUNC_DB_BY_ADDR = {}
struct_types = {}
struct_instances = {}


def set_funcdb(db):
    global FUNC_DB, FUNC_DB_BY_ADDR
    # index by name in addition to by addr
    for addr, props in list(db.items()):
        FUNC_DB[props["label"]] = props
    FUNC_DB_BY_ADDR = db


REG_PROPS = [
    "callsites_live_out", "modifieds", "preserveds", "reach_exit", "args", "estimated_args",
    "returns",
]

def preprocess_funcdb(FUNC_DB):
    for addr, props in FUNC_DB.items():
        for prop in REG_PROPS:
            if prop in props:
                props[prop] = set(core.REG(x) for x in props[prop])


def postprocess_funcdb(FUNC_DB):
    for addr, props in FUNC_DB.items():
        for prop in REG_PROPS:
            if prop in props:
                props[prop] = sorted([x.name for x in props[prop]], key=core.natural_sort_key)


def load_funcdb(fname):
    with open(fname) as f:
        FUNC_DB = yaml.load(f)
        preprocess_funcdb(FUNC_DB)
        set_funcdb(FUNC_DB)


def save_funcdb(fname, backup=True):
    global FUNC_DB_BY_ADDR
    postprocess_funcdb(FUNC_DB_BY_ADDR)
    if backup and os.path.exists(fname):
        os.rename(fname, fname + ".bak")

    with open(fname, "w") as f:
        yaml.dump(FUNC_DB_BY_ADDR, f)


def set_struct_types(data):
    global struct_types
    struct_types = data


def set_struct_instances(data):
    global struct_instances
    struct_instances = data


def get_struct_types():
    global struct_types
    return struct_types


def get_struct_instances():
    global struct_instances
    return struct_instances
