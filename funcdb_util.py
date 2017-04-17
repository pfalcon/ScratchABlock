#!/usr/bin/env python3
import sys
import os
import argparse

import yaml

import yamlutils


argp = argparse.ArgumentParser(description="Perform various transformations on a function database")
argp.add_argument("command", help="transformation to perform")
argp.add_argument("file", help="function database file (YAML)")
args = argp.parse_args()

with open(args.file) as f:
    FUNC_DB = yaml.load(f)

label2addr = {}

for addr, props in FUNC_DB.items():
    label2addr[props["label"]] = addr


if args.command == "label2addr":

    for addr, props in FUNC_DB.items():
        props["calls_addr"] = [label2addr.get(x, x) for x in props["calls"]]

elif args.command == "addr2label":
    for addr, props in FUNC_DB.items():
        print(addr)
        props["calls"] = [FUNC_DB[x]["label"] if x in FUNC_DB else x for x in props["calls_addr"]]

elif args.command == "called_by":
    called = {}

    for addr, props in FUNC_DB.items():
        calls_unk = []
        name = props["label"]
        for callee in props.get("calls", []):
            called.setdefault(callee, set()).add(name)
            if callee not in label2addr:
                calls_unk.append(callee)
        if calls_unk:
            props["calls_unk"] = calls_unk

    for addr, props in FUNC_DB.items():
        name = props["label"]
        if name in called:
            props["called_by"] = called[name]

else:
    argp.error("Unknown command: " + args.command)

os.rename(args.file, args.file + ".bak")

with open(args.file, "w") as f:
    yaml.dump(FUNC_DB, f)
