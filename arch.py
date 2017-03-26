import os.path
from core import REG

import yaml


BITNESS = 32
ENDIANNESS = "LITTLE"

FUNC_DB = {}


def reg_range(first, last):
    return {REG("a%d" % x) for x in range(first, last + 1)}

ALL_REGS = reg_range(0, 15)


def call_args(addr):
    return reg_range(2, 7)

def call_ret(addr):
    return reg_range(2, 5)

def call_save(addr):
    return reg_range(12, 15) | {REG("sp")}

def call_uses(addr):
    return call_args(addr)

def call_defs(addr):
    return call_ret(addr) | (ALL_REGS - call_save(addr))


def ret_uses(cfg):
    # a0 contains return address
    # sp should be preserved across call, but we'll check that using sp0 pseudo-reg.
    #return {REG("a0"), REG("sp")}
    if cfg and cfg.props["name"] in FUNC_DB:
        regs = FUNC_DB[cfg.props["name"]]["ret"]
        assert isinstance(regs, list)
        return set(map(REG, regs))
    return {REG("a0")}


if os.path.exists("funcdb.yaml"):
    #print("Loading function database")
    with open("funcdb.yaml") as f:
        FUNC_DB = yaml.load(f)
