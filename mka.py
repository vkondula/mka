#!/bin/python3.4
# coding=utf-8
#MKA:xkondu00
import os
import sys
import argparse
from configparser import ConfigParser
from stateMachine import FiniteStateMachine as FST

def parse_args(parser):
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--input",
        help="Read from this file instead of stdin",
        default="-",
        type=str)
    parser.add_argument(
        "--output",
        help="Write to this file instead of stdout",
        default="-",
        type=str)
    group.add_argument(
        "-f", "--find-non-finishing",
        help="Prints out all non finishing states, '0' if no state is found",
        action="store_true")
    group.add_argument(
        "-m", "--minimaze",
        help="Minimaze finite state machine",
        action="store_true")
    parser.add_argument(
        "-i", "--case-insensitive",
        help="Symbols and state names are case insensitive",
        action="store_true")
    parser.add_argument(
        "-w", "--white-char",
        help="Commas can be replaced by white characters",
        action="store_true")
    parser.add_argument(
        "-r", "--rules-only",
        help="Expects rules only. First state given is starting",
        action="store_true")
    group.add_argument(
        "--analyze-string",
        help="Check if given string can be read by state machine",
        type=str)
    parser.add_argument(
        "--wsfa",
        help="Simple deterministic finite state machine could be given",
        action="store_true")
    try:
        args = parser.parse_args()
    except SystemExit:
        # changing return value from 2 to 1
        sys.exit(1)
    if args.input == "-":
        args.input = sys.stdin
    else:
        try:
            args.input = os.path.expanduser(args.input)
            args.input = open(os.path.realpath(args.input), "r")
        except IOError or OSError:
            sys.stderr.write("Could not open file\n")
            return 2
    if args.output == "-":
        args.output = sys.stdout
    else:
        try:
            args.output = os.path.expanduser(args.output)
            args.output = open(os.path.realpath(args.output), "w")
        except IOError or OSError:
            sys.stderr.write("Could not open file\n")
            return 3
    return args

def main(args):
    if not args.rules_only:
        state_fst = FST(rules_only=True)
        conf = ConfigParser()
        conf.read("state.conf")
        state_fst.build_from_config(conf)
        state_fst.set_starting("start")
        state_fst.read_string("(  {ad,q1_q1 , wqe#fml\n,e}")
        print(state_fst.get_output())
        print("is finishing: %s" %state_fst.is_finishing())
        print(state_fst.current.get_name())
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_args(parser)
    if type(args) == int:
        sys.exit(args)
    retval = main(args)
    sys.exit(retval)