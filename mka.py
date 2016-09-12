#!/bin/python3.4
# coding=utf-8
#MKA:xkondu00
import os
import sys
import argparse
import stateMachine as SM
from configparser import ConfigParser
from stateMachine import FiniteStateMachine as FSM

CLASSIC_FSM = "classic.conf.py"
RULES_ONLY_FSM = "rules_only.conf.py"
WHITE_CHAR_FSM = "white_char.conf.py"


class WrongArgument(BaseException):
    pass


def parse_args(parser):
    """
    Handles CLI options using argparse
    """
    if "--help" in sys.argv and len(sys.argv) != 2:
        sys.stderr.write("Incorrect combination of parameters\n")
        return 1
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--input",
        help="Read from this file instead of stdin",
        action="append",
        type=str)
    parser.add_argument(
        "--output",
        help="Write to this file instead of stdout",
        action="append",
        type=str)
    group.add_argument(
        "-f", "--find-non-finishing",
        help="Prints out non finishing state, '0' if no state is found",
        action="append_const",
        const=True)
    group.add_argument(
        "-m", "--minimize",
        help="Minimize finite state machine",
        action="append_const",
        const=True)
    parser.add_argument(
        "-i", "--case-insensitive",
        help="Symbols and state names are case insensitive",
        action="append_const",
        const=True)
    parser.add_argument(
        "-w", "--white-char",
        help="Commas can be replaced by white characters",
        action="append_const",
        const=True)
    parser.add_argument(
        "-r", "--rules-only",
        help="Expects rules only. First state given is starting",
        action="append_const",
        const=True)
    group.add_argument(
        "--analyze-string",
        help="Check if given string can be read by state machine",
        type=str,
        action='append',)
    parser.add_argument(
        "--wsfa",
        help="Simple deterministic finite state machine could be given",
        action="append_const",
        const=True)
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # changing return value from 2 to 1
        # return 0 if --help
        sys.exit(1 if e.code else 0)
    # checking duplicity of arguments
    for key in args.__dict__:
        args.__dict__[key] = argument_param(args.__dict__[key], None)
    # setting input stream
    if args.input is None or args.input == "-":
        args.input = sys.stdin
    else:
        try:
            args.input = os.path.expanduser(args.input)
            args.input = open(
                os.path.realpath(args.input),
                "r", encoding="utf-8"
                )
        except IOError or OSError:
            sys.stderr.write("Could not open file\n")
            return 2
    # setting output stream
    if args.output is None or args.output == "-":
        args.output = sys.stdout
    else:
        try:
            args.output = os.path.expanduser(args.output)
            args.output = open(
                os.path.realpath(args.output),
                "w", encoding="utf-8"
                )
        except IOError or OSError:
            sys.stderr.write("Could not open file\n")
            return 3
    return args


def argument_param(argv, default):
    if type(argv) == list:
        if len(argv) != 1:
            sys.stderr.write("Duplicity of argument\n")
            sys.exit(1)
        else:
            return argv[0]
    elif type(argv) == bool:
        return argv
    return default


def input_parsing_fsm(conf_path, starting_state, fd):
    """
    Builds FSM from given config file
    Reads input from file or stdin
    Returns: dictionery of FA's components created by handler
    """
    state_fsm = FSM(rules_only=True)
    conf = ConfigParser()
    conf.read(conf_path)
    state_fsm.build_from_config(conf)
    state_fsm.set_starting(starting_state)
    while True:
        char = fd.read(1)
        if char == "":
            break
        state_fsm.step(char)
    if not state_fsm.is_finishing():
        raise SM.NotFinishing("Lexial or syntax error", "\n")
    state_fsm.step(" ")
    return state_fsm.get_output()


def createFSM(configuration, case_insensitive=False, rules_only=False):
    """
    Creates FSM object and fills it with components.

    parametrs:
        configuration: FA's components in dictionary
    """
    list_of_states = configuration.get("state", [])
    list_of_symbols = configuration.get("symbol", [])
    list_of_rules = zip(
        configuration.get("current", []),
        configuration.get("target", []),
        configuration.get("input", [])
    )
    if not rules_only:
        start = configuration.get("start").pop()
        list_of_finishing = configuration.get("finish", [])
    else:
        start = configuration.get("current", [])[0]
        list_of_finishing = configuration.get("finish", [])
        list_of_finishing = list(set([
            x[0] for x in zip(
                configuration.get("target", []),
                list_of_finishing
            )
            if x[1] == "."
        ]))
    fsm = FSM(rules_only=rules_only, line_comment=None)
    # add all states
    for item in list_of_states:
        if case_insensitive:
            item = item.lower()
        fsm.add_state(item)
    # add all symbols
    if not list_of_symbols and not rules_only:
        raise SM.Invalid("Set of symbols is empty", "\n")
    for item in list_of_symbols:
        if case_insensitive:
            item = item.lower()
        fsm.add_symbol(item)
    # add rules
    for item in list_of_rules:
        if item[2] == "'":
            raise SM.Nondeterminism("Epsilon transitions", "\n")
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
    """
    1) set correct config file for lexical and syntax analysis
    2) read input (return 60 if syntax or lexical error)
    3) create FSM object (return 61 if semantic error)
    4) check if FSM is well specified (return 62 otherwise)
    5) based of CLI options evaluate FSM
        a) write to output
        b) minimize
        c) find non finihsing state
        d) analyze string
    """
    if args.rules_only:
        fsm_conf = RULES_ONLY_FSM
    elif args.white_char:
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
    except (SM.Nondeterminism) as e:
        sys.stderr.write(" ".join(e.args))
        sys.exit(62)

    if args.wsfa:
        # TODO
        pass

    # Evaluate FSM
    if not fsm.is_WSFA():
        sys.stderr.write("Not well specified finit automata\n")
        sys.exit(62)
    if args.minimize:
        fsm = fsm.minimize()
    if args.analyze_string:
        if args.case_insensitive:
            args.analyze_string = args.analyze_string.lower()
        try:
            correct = fsm.read_string(args.analyze_string)
        except SM.MissingRule:
            return 1
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
