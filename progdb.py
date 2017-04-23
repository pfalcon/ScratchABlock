#
# This module deals with various "program databases" as required
# for analysis passes. Among them: function database (funcdb.yaml),
# databases of structures, etc.
#
import os.path

import yaml
import yamlutils

import utils
import core
from core import is_addr, is_value, is_expr


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
                props[prop] = sorted([x.name for x in props[prop]], key=utils.natural_sort_key)


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


def update_funcdb(cfg):
    "Aggregate data from each CFG processed into a function DB."
    if "addr" not in cfg.props:
        return
    func_props = FUNC_DB_BY_ADDR.setdefault(cfg.props["addr"], {})
    func_props["label"] = cfg.props["name"]

    for prop in ("args", "estimated_args", "modifieds", "preserveds", "reach_exit"):
        if prop in cfg.props:
            func_props[prop] = cfg.props[prop]

    for prop in ("calls", "func_refs", "mmio_refs"):
        if prop in cfg.props:
            def ext_repr(x):
                if is_addr(x):
                    return x.addr
                if is_value(x):
                    return hex(x.val)
                if is_expr(x):
                    if x.op == "+" and len(x.args) == 2:
                        if is_value(x.args[1]):
                            x = EXPR("+", [x.args[1], x.args[0]])
                    return str(x)
                assert False, repr(x)
            func_props[prop] = sorted([ext_repr(x) for x in cfg.props[prop]])


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
