#!/usr/bin/env python3
import sys
import os
import argparse

import yaml


argp = argparse.ArgumentParser(description="Perform various transformations on a function database")
argp.add_argument("command", help="transformation to perform")
argp.add_argument("file", help="function database file (YAML)")
args = argp.parse_args()

with open(args.file) as f:
    FUNC_DB = yaml.load(f)

if args.command == "label2addr":
    label2addr = {}

    for addr, props in FUNC_DB.items():
        label2addr[props["label"]] = addr

    for addr, props in FUNC_DB.items():
        props["calls_addr"] = [label2addr.get(x, x) for x in props["calls"]]

elif args.command == "addr2label":
    for addr, props in FUNC_DB.items():
        print(addr)
        props["calls"] = [FUNC_DB[x]["label"] if x in FUNC_DB else x for x in props["calls_addr"]]


os.rename(args.file, args.file + ".bak")

with open(args.file, "w") as f:
    yaml.dump(FUNC_DB, f)
