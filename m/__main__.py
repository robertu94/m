#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .plugins import *
from .plugins.Base import MBuildTool

import argparse
import itertools
import shlex

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmdline", "-c", action="append", default=list())
    parser.set_defaults(action=lambda m: m.build())

    sp = parser.add_subparsers()

    test = sp.add_parser("test", aliases=["t"])
    test.set_defaults(action=lambda m: m.test())

    clean = sp.add_parser("clean", aliases=["c"])
    clean.set_defaults(action=lambda m: m.clean())

    build = sp.add_parser("build", aliases=['b'])
    build.set_defaults(action=lambda m: m.build())

    install = sp.add_parser("install", aliases=['i'])
    install.set_defaults(action=lambda m: m.install())

    build = sp.add_parser("settings", aliases=['s'])
    build.set_defaults(action=lambda m: m.settings())

    return parser.parse_args()

def main():
    args = parse_args()
    args.cmdline = list(itertools.chain(*[shlex.split(arg) for arg in args.cmdline]))
    tool = MBuildTool(args)
    args.action(tool)


if __name__ == "__main__":
    main()
