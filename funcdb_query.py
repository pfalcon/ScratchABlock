#!/usr/bin/env python3
import sys
import os
import argparse

import yaml

import yamlutils


argp = argparse.ArgumentParser(description="Query a function database")
argp.add_argument("file", help="function database file (YAML)")
argp.add_argument("--select", help="fields to select")
argp.add_argument("--where", help="condition of rows to select")
argp.add_argument("--sort", action="store_true", help="sort resultset")
args = argp.parse_args()

with open(args.file) as f:
    FUNC_DB = yaml.load(f)


def where(props):
    #print("where", props)
    try:
        res = eval(args.where, None, props)
    except NameError:
        return False
    return res

def select(props):
    #print("select", props)
    if args.select == "*":
        return props
    res = eval("(" + args.select + ")", None, props)
    return res

res = []
for addr, props in FUNC_DB.items():
    props = props.copy()
    props["addr"] = addr
    if where(props):
        res.append(select(props))

if args.sort:
    res.sort()

for row in res:
    if isinstance(row, dict):
        print(row)
    else:
        row = [str(x) for x in row]
        print(": ".join(row))
