from core import ADDR, REG
from archutils import *


BITNESS = 32
ENDIANNESS = "big"

ALL_REGS = {REG("r0"), REG("sp"), REG("rtoc")} | reg_range("r", 3, 31)


def call_params(addr):
    return reg_range("r", 3, 10)


def param_filter(regs):
    # Assume for now that all parameters will be passed in registers.
    # This must be good enough to cover the most usage cases.
    # The following cases will break it:
    # - functions accepting more then 8 params
    # - functions accepting floating-point params
    # - variadic functions
    return reg_continuous_subrange(regs, reg_range("r", 3, 10))


def call_ret(addr):
    return {REG("r3")}


def ret_filter(regs):
    # Assuming there is no floating-point stuff
    return {REG("r3")}


def call_save(addr):
    return reg_range("r", 13, 31) | {REG("sp")}


def call_defs(addr):
    return call_ret(addr) | (ALL_REGS - call_save(addr))


def ret_uses(cfg):
    return set()
