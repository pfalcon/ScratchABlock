"Module to deal with (binary) data of analyzed code."

import glob
import re
from collections import namedtuple


AreaTuple = namedtuple("AreaTuple", ["start", "end", "data", "props"])

AREAS = []


class InvalidAddrException(Exception):
    "Thrown when dereferencing address which doesn't exist in address space."
    def __init__(self, addr):
        self.args = (addr, hex(addr))


def init(dir):
    "Initialize and load binary data structures."
    for fname in glob.glob(dir + "/*.bin"):
        m = re.search(r".+/([0-9A-Fa-f]+)-([0-9A-Fa-f]+)(-([A-Za-z]+))?", fname)
        if not m:
            continue
        with open(fname, "rb") as f:
            data = f.read()
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        access = m.group(4).upper()
        AREAS.append(AreaTuple(start, end, data, {"access": access}))
    AREAS.sort()


def addr2area(addr):
    for a in AREAS:
        if a.start <= addr < a.end:
            return (addr - a.start, a)
    return (None, None)


def get_bytes(addr, sz):
    off, area = addr2area(addr)
    if area is None:
        raise InvalidAddrException(addr)
    return area.data[off:off + sz]


def deref(addr, bits):
    # TODO: hardcodes little-endian
    res = 0
    bcnt = 0
    for b in get_bytes(addr, bits // 8):
        res |= b << bcnt
        bcnt += 8
    return res


if __name__ == "__main__":
    init(".")
    print(hex(deref(0x40000054, 32)))
