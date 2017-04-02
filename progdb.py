

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
