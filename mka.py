#!/bin/python3.4
# coding=utf-8
# MKA:xkondu00
import os
import sys
import argparse
import stateMachine as SM
from configparser import ConfigParser
from stateMachine import FiniteStateMachine as FSM

CLASSIC_FSM = "classic.conf"
RULES_ONLY_FSM = "rules_only.conf"
WHITE_CHAR_FSM = "white_char.conf"


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
        "-m", "--minimize",
        help="Minimize finite state machine",
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
        type=str,
        default=None)
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


def input_parsing_fsm(conf_path, starting_state, fd):
    state_fsm = FSM(rules_only=True)
    conf = ConfigParser()
    conf.read(conf_path)
    state_fsm.build_from_config(conf)
    state_fsm.set_starting(starting_state)
    while not state_fsm.is_finishing():
        char = fd.read(1)
        if char == "":
            break
        state_fsm.step(char)
    if not state_fsm.is_finishing():
        raise SM.NotFinishing("Lexial or syntax error", "\n")
    return state_fsm.get_output()

def createFSM(configuration, case_insensitive = False, rules_only = False):
    list_of_states = configuration.get("state", [])
    list_of_symbols = configuration.get("symbol", [])
    list_of_rules = zip(
        configuration.get("current", []),
        configuration.get("target", []),
        configuration.get("input", [])
    )
    list_of_finishing = configuration.get("finish", [])
    start = configuration.get("start").pop()
    print(list_of_states)
    print(list_of_symbols)
    print("start: %s" % start)
    print(list_of_finishing)
    fsm = FSM(rules_only = rules_only)
    # add all states
    for item in list_of_states:
        if case_insensitive:
            item = item.lower()
        fsm.add_state(item)
    # add all symbols
    if not list_of_symbols:
        raise SM.Invalid("Set of symbols is empty", "\n")
    for item in list_of_symbols:
        if case_insensitive:
            item = item.lower()
        fsm.add_symbol(item)
    # add rules
    for item in list_of_rules:
        if case_insensitive:
            fsm.add_rule(item[0].lower(), item[1].lower(), item[2].lower())
        else:
            fsm.add_rule(item[0], item[1], item[2])
    # set starting
    fsm.set_starting(start)
    # set finishing
    for item in list_of_finishing:
        if case_insensitive:
            item = item.lower()
        fsm.set_finishing(item)
    return fsm


def main(args):
    if args.rules_only:
        fsm_conf = RULES_ONLY_FSM
    if args.white_char:
        fsm_conf = WHITE_CHAR_FSM
    else:
        fsm_conf = CLASSIC_FSM
    # Prepare input readinf FSM
    try:
        config = input_parsing_fsm(fsm_conf, "start_1", args.input)
    except (SM.NotFinishing, SM.MissingRule) as e:
        sys.stderr.write(" ".join(e.args))
        sys.exit(60)

    # Fill FSM with states, symbols and rules
    try:
        fsm = createFSM(config, args.case_insensitive, args.rules_only)
    except (SM.Invalid) as e:
        sys.stderr.write(" ".join(e.args))
        sys.exit(61)

    if args.wsfa:
        # TODO
        pass

    # Evaluate FSM
    if not fsm.is_WSFA():
        sys.stderr.write("Not well specified finit automata\n")
        sys.exit(62)
    if args.minimize:
        # TODO
        fsm.minimize()
    if args.analyze_string:
        if args.case_insensitive:
            args.analyze_string = args.analyze_string.lower()
        correct = fsm.read_string(args.analyze_string)
        args.output.write("1" if correct else "0")
    elif not args.find_non_finishing:
        args.output.write(repr(fsm))
    else:
        args.output.write(fsm.find_non_terminating())
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
