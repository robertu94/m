#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""main entrypoint for MTool"""

import argparse
import itertools
import shlex
import logging

from .plugins.Base import MBuildTool


MODES = ('build', 'clean', 'test', 'install', 'settings')


def parse_args():
    """parse the command line arguments"""

    parser = argparse.ArgumentParser()
    # default mode
    parser.add_argument("--cmdline_build", "-c",
        action="append", default=list())
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.set_defaults(action=lambda m: m.build())

    subparsers = parser.add_subparsers()

    # all the other modes
    for mode in MODES:
        mode_parser = subparsers.add_parser(mode, aliases=[mode[0]])

        # using the lambda with default argument creates a new scope which
        # captures the mode mode variable by value instead of by reference
        # which would otherwise cause all of the iterations of the loop to have
        # the same value
        mode_parser.set_defaults(
            action=lambda m, mode=mode: getattr(m, mode)())

        mode_parser.add_argument(f"--cmdline_{mode}",
                                 "-c", action="append", default=list())
        parser.add_argument(f"--{mode}_arg",
                            action="append", default=list())

    return parser.parse_args()


def main():
    """main entry point for MTool"""
    args = parse_args()

    for mode in MODES:
        setattr(args, "cmdline_{mode}".format(mode=mode), list(
            itertools.chain(
                *[shlex.split(arg) for arg in
                itertools.chain(
                    getattr(args, f"cmdline_{mode}", []),
                    getattr(args, f"{mode}_arg", []))])
            ))
        delattr(args, f"{mode}_arg")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 0 else logging.INFO)

    tool = MBuildTool(args)
    args.action(tool)


if __name__ == "__main__":
    main()
