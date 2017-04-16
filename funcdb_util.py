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

elif args.command == "called_by":
    calls = {}
    for addr, props in FUNC_DB.items():
        name = props["label"]
        for callee in props.get("calls", []):
            calls.setdefault(callee, set()).add(name)

    for addr, props in FUNC_DB.items():
        name = props["label"]
        if name in calls:
            props["called_by"] = calls[name]


os.rename(args.file, args.file + ".bak")

with open(args.file, "w") as f:
    yaml.dump(FUNC_DB, f)
