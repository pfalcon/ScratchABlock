#!/usr/bin/env python3
import sys
import os
import glob


def process_file(fname):
    func_name = None

    with open(fname) as f:
        l = f.readline()
        l = l.strip()
        addr, label = l.split(None, 1)
        assert label[-1] == ":", "File %s must start with a label" % fname
        if not label.startswith("loc_"):
            return

        for l in f:
            l = l.strip()
            addr, label = l.split(None, 1)
            if label[-1] == ":" and not label.startswith("loc_"):
                func_name = label[:-1]

    assert func_name
    print("Processing:", fname)

    os.rename(fname, fname + ".bak")

    with open(fname + ".bak") as f, open(fname, "w") as f_out:
        l = f.readline()
        addr, rest = l.split(None, 1)
        f_out.write("%s.0 %s:\n" % (addr, func_name))
        f_out.write("%s.0 goto %s.0\n" % (addr, func_name))
        f_out.write(l)
        for l in f:
            addr, label = l.split(None, 1)
            label = label.strip()
            if label[-1] == ":" and not label.startswith("loc_"):
                this_name = label[:-1]
                if func_name == this_name:
                    l = l.replace(func_name, func_name + ".0")
            f_out.write(l)


if __name__ == "__main__":

    if os.path.isdir(sys.argv[1]):
        for full_name in glob.glob(sys.argv[1] + "/*"):
            if full_name.endswith(".lst") and os.path.isfile(full_name):
                process_file(full_name)
    else:
        process_file(sys.argv[1])
