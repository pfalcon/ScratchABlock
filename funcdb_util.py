#!/usr/bin/env python3
import sys
import os
import argparse

import yaml

import yamlutils


argp = argparse.ArgumentParser(description="Perform various transformations on a function database")
argp.add_argument("file", help="function database file (YAML)")
argp.add_argument("command", help="transformation to perform")
argp.add_argument("args", nargs="*", help="transformation arguments (optional)")
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

elif args.command == "returns":
    for addr, props in FUNC_DB.items():
        if "modifieds" in props and "callsites_live_out" in props:
            props["returns"] = set(props["modifieds"]) & set(props["callsites_live_out"])

elif args.command == "select-subgraph":
    if len(args.args) > 1:
        dirname = args.args[1]
    else:
        dirname = args.args[0] + ".subgraph"
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    else:
        print("Warning: already exists:", dirname)

    queue = [args.args[0]]
    seen = set()
    while queue:
        func = queue.pop()
        if func in seen:
            continue
        seen.add(func)
        addr = label2addr[func]
        funcinfo = FUNC_DB[addr]
        print(func)
        #print(funcinfo)
        queue.extend(funcinfo["calls"])
        fname = "%s-%s.lst" % (addr, func)
        try:
            os.symlink("../funcs/" + fname, dirname + "/" + fname)
        except FileExistsError as e:
            print("Warning:", e)

else:
    argp.error("Unknown command: " + args.command)

os.rename(args.file, args.file + ".bak")

with open(args.file, "w") as f:
    yaml.dump(FUNC_DB, f)
