#!/bin/python3.4
# coding=utf-8
# MKA:xkondu00
import os
import sys
import argparse
import stateMachine
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


def input_parsing_fst(conf_path, starting_state, fd, until_eof):
    state_fst = FST(rules_only=True)
    conf = ConfigParser()
    conf.read(conf_path)
    state_fst.build_from_config(conf)
    state_fst.set_starting(starting_state)
    while not state_fst.is_finishing() or until_eof:
        char = fd.read(1)
        if char == "":
            break
        state_fst.step(char)
    if not state_fst.is_finishing():
        raise stateMachine.NotFinishing()
    return state_fst.get_output()


def main(args):
    if not args.rules_only:
        states = input_parsing_fst(
            "state.conf", "start", args.input, False)
        list_of_states = states.get("1", [])

        alphabet = input_parsing_fst(
            "alphabet.conf", "start", args.input, False)
        list_of_symbols = alphabet.get("2", [])

        rules = input_parsing_fst("rules.conf", "start", args.input, False)
        list_of_rules = zip(
            rules.get("state", []),
            rules.get("target", []),
            rules.get("symbol", [])
        )

        finishing = input_parsing_fst("finishing.conf", "start", args.input, True)
        list_of_finishing = finishing.get("finish", [])
        start = finishing.get("start").pop()
        print(list_of_states)
        print(list_of_symbols)
        print("start: %s" %start)
        print(list_of_finishing)
        fst = FST()
        for item in list_of_states:
            fst.add_state(item)
        for item in list_of_symbols:
            fst.add_symbol(item)
        for item in list_of_rules:
            fst.add_rule(item[0], item[1], item[2])
        fst.set_starting(start)
        for item in list_of_finishing:
            print("WTF", item)
            fst.set_finishing(item)
        print("is WFSA: %s" %fst.is_WFSA())
        if not args.find_non_finishing:
            args.output.write(repr(fst))
        else:
            args.output.write(fst.find_non_terminating())
    args.input.close()
    args.output.close()
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_args(parser)
    if type(args) == int:
        sys.exit(args)
    retval = main(args)
    sys.exit(retval)
