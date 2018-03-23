#!/usr/bin/env python3
import sys
import os
import argparse

import yaml

import yamlutils


argp = argparse.ArgumentParser(description="Query a function database")
argp.add_argument("file_or_dir", help="function database file (YAML) or project directory")
argp.add_argument("--select", help="fields to select")
argp.add_argument("--where", help="condition of rows to select")
argp.add_argument("--sort", action="store_true", help="sort resultset")
argp.add_argument("--html", action="store_true", help="output HTML")
args = argp.parse_args()

if not args.select and not args.where:
    argp.error("At least one of --select or --where should be given")

if os.path.isdir(args.file_or_dir):
    args.file_or_dir += "/funcdb.yaml"

with open(args.file_or_dir) as f:
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

if args.html:
    print("<html><body><table border='1' cellspacing='0'>")

for row in res:
    if isinstance(row, dict):
        if args.html:
            print("<tr><td>" + row + "</td></tr>")
        else:
            print(row)
    else:
        row = [str(x) for x in row]
        if args.html:
            print("<tr><td>" + "</td><td>".join(row) + "</td></tr>")
        else:
            print(": ".join(row))

if args.html:
    print("</table></body></html>")
