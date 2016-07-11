from core import REG

BITNESS = 32
ENDIANNESS = "LITTLE"


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


def ret_uses():
    # a0 contains return address, and sp should be preserved across
    # call, so depend on it also.
    return {REG("a0"), REG("sp")}
