#!/bin/python3.4
# coding=utf-8
# MKA:xkondu00

from copy import copy


class Redefinition(BaseException):
    pass


class Invalid(BaseException):
    pass


class MissingRule(BaseException):
    pass


class NotFinishing(BaseException):
    pass


class FiniteStateMachine(object):

    def __init__(
        self,
        rules_only=False,
        line_comment="#",
        post_comment=" ",
        allow_redefinition=True,
        escape_state="left_ap"
    ):
        self.rules_only = rules_only
        self.can_redef = allow_redefinition
        self.literally = escape_state
        self.states = dict()
        self.alphabet = list()
        self.current = None
        self.buffer = str()
        self.last_handler = None
        self.output = dict()
        # for comment in input
        self.line_comment = line_comment
        self.post_comment = post_comment
        self.in_line_comment = False
        # for WSFA check
        self.reversed_rules = dict()
        self.dump_rules = dict()
        self.finishing = list()

    def __repr__(self):
        # states
        states = list(self.states.keys())
        states.sort()
        states = ", ".join(states)
        # alphabet
        self.alphabet.sort()
        alphabet = list()
        for symbol in self.alphabet:
            alphabet.append("'%s'" % symbol)
        alphabet = ", ".join(alphabet)
        # rules
        rules = list()
        for state_name in self.states:
            state = self.states[state_name]
            for symbol in state.rules:
                target_name = state.rules[symbol][0].get_name()
                rules.append("%s '%s' -> %s" %
                             (state_name, symbol, target_name))
        rules.sort()
        rules = ",\n".join(rules)
        # starting
        starting = self.current.get_name()
        # finishing
        self.finishing.sort()
        finishing = ", ".join(self.finishing)
        # concatenate
        return ("(\n{%s},\n{%s},\n{\n%s\n},\n%s,\n{%s}\n)" %
                (states, alphabet, rules, starting, finishing))

    __str__ = __repr__

    def add_state(self, name, finishing=False):
        if (name in self.states):
            if self.rules_only or self.can_redef:
                return False
            raise Redefinition("Multiple states with name: %s" % name, "\n")

        self.states[name] = State(name, finishing)
        return True

    def add_rule(self, starting_name, target_name, symbol, returning=False):
        if not self.rules_only:
            if (starting_name not in self.states or
                    target_name not in self.states or
                    symbol not in self.alphabet
                    ):
                raise Invalid("Missing state or symbol in definition", "\n")
        else:
            self.add_state(starting_name)
            self.add_state(target_name)
            self.add_symbol(symbol)
        target = self.states[target_name]
        symbol = self._symbol_decode(symbol)
        retval = self.states[starting_name].add_rule(symbol, target, returning)
        if retval:
            self._add_dump_rule(starting_name, target_name)
        return retval

    def add_symbol(self, symbol):
        if (self._symbol_collision(symbol)) and not self.rules_only:
            if self.can_redef:
                return False
            raise Redefinition("Symbol %s already declared" % symbol, "\n")
        if type(symbol) is tuple or type(symbol) is list:
            self.alphabet += symbol
        else:
            self.alphabet.append(symbol)
        return True

    def set_finishing(self, name):
        if name in self.states:
            self.finishing.append(name)
            state = self.states[name]
            state.set_finishing()
        else:
            raise Invalid("Finishing doens't exists", "\n")

    def _symbol_collision(self, symbol):
        if (type(symbol) is not tuple and type(symbol) is not list):
            if symbol in self.alphabet:
                return True
        return False

    def set_starting(self, name):
        if name in self.states:
            self.current = self.states[name]
        else:
            raise Invalid("Starting state doesn't exists", "\n")

    def build_from_config(self, conf):
        self.rules_only = True
        for state in conf:
            if state == "DEFAULT":
                continue

            finishing = False
            name = state
            if state[-1] == ".":
                name = state[:-1]
                finishing = True

            if name not in self.states:
                self.add_state(name)
            if finishing:
                self.set_finishing(name)

            for target in conf[state]:
                if target not in self.states:
                    self.add_state(target)
                trans = conf[state][target].split("\n")
                if len(trans) != 2:
                    ret = None
                else:
                    ret = trans[1]
                self.add_rule(name, target, trans[0], ret)

    def is_finishing(self):
        return self.current.is_finishing()

    def is_WSFA(self):
        starting = list(self.current.get_name())
        state_count = len(self.states)
        symbol_count = len(self.alphabet)
        if not self._all_accessible() or not self.find_non_terminating():
            return False
        for state in self.states:
            if symbol_count != len(self.states[state].rules):
                return False
            for symbol in self.states[state].rules:
                if symbol == "'":
                    return False
        return True

    def find_non_terminating(self):
        """
        Returns one of:
            1) name of non-terminating state
            2) "0" if no non-terminating state exists
            3) False if more than one non-terminating state exists
        """
        starting = copy(self.finishing)
        while True:
            changed = False
            for state in starting:
                targets = self.reversed_rules.get(state, [])
                for target in targets:
                    if target not in starting:
                        starting.append(target)
                        changed = True
            if not changed:
                break
        non_terminating = "0"
        for state in self.states:
            if state not in starting:
                if non_terminating == "0":
                    non_terminating = state
                else:
                    return False
        return non_terminating

    def minimize(self):
        pass

    def step(self, char):
        if self.line_comment == char:
            if self.literally not in self.current.get_name():
                self.in_line_comment = True
                return self.current
        if self.in_line_comment:
            if char == "\n":
                self.in_line_comment = False
                return self.step(self.post_comment)
            return self.current

        if not self.current:
            raise Invalid("Starting state not set", "\n")

        retval = self.current.step(char)
        if retval is None:
            raise MissingRule("Missing rule for: '%s' ord(%s) at state: %s\n"
                              % (char, ord(char), self.current.get_name()))
        self.current = retval[0]
        self._handle_output(char, retval[1])
        return retval[0]

    def _symbol_decode(self, symbol):
        if len(symbol) > 1 and symbol[0] == "!":
            return SymbolGroup(symbol)
        return symbol

    def _handle_output(self, char, handler):
        if self.last_handler and self.last_handler != handler:
            if self.last_handler not in self.output:
                self.output[self.last_handler] = list()
            self.output[self.last_handler].append(self.buffer)
            self.buffer = str()
        if handler:
            self.buffer += char
        self.last_handler = handler

    def get_output(self):
        return self.output

    def read_string(self, string):
        try:
            for char in string:
                self.step(char)
            return self.is_finishing()
        except MissingRule:
            return False

    def _add_dump_rule(self, state, target):
        if state not in self.dump_rules:
            self.dump_rules[state] = list()
        if target not in self.dump_rules[state]:
            self.dump_rules[state].append(target)

        if target not in self.reversed_rules:
            self.reversed_rules[target] = list()
        if state not in self.reversed_rules[target]:
            self.reversed_rules[target].append(state)

    def _all_accessible(self):
        accessible = list(self.current.get_name())
        while True:
            changed = False
            for state in accessible:
                targets = self.dump_rules.get(state, [])
                for target in targets:
                    if target not in accessible:
                        accessible.append(target)
                        changed = True
            if not changed:
                break
        return len(accessible) == len(self.states)


class State(object):

    def __init__(self, name, finishing):
        self.name = name
        self.finishing = finishing
        self.rules = dict()

    def add_rule(self, symbol, target, returning):
        if symbol in self.rules:
            if target is self.rules[symbol][0]:
                if can_redef:
                    return False
                raise Redefinition("%s in %s" % (symbol, self.name), "\n")
            else:
                raise Invalid(
                    "Multiple targets for one symbol... nondeterminism", "\n")
        self.rules[symbol] = (target, returning)
        return True

    def finishing(self):
        return self.finishing

    def step(self, char):
        for key in self.rules:
            if type(key) is SymbolGroup:
                if key(char):
                    retval = self.rules[key]
                    return retval
            elif char == key:
                retval = self.rules[key]
                return retval
        return None

    def get_name(self):
        return self.name

    def set_finishing(self):
        self.finishing = True

    def is_finishing(self):
        return self.finishing


class SymbolGroup(object):

    def __init__(self, group):
        self.group = group

    def __call__(self, char):
        return {
            "!ALPHA": char.isalpha(),
            "!ALPHANUM": char.isalnum(),
            "!ALPHANUM_": char.isalnum() or char == "_",
            "!SPACE": char.isspace(),
            "!LF": char in "\n\r",
            "!SKIP": char not in "\n\r",
            "!NOTAPOST": char != "'"
        }[self.group]

    def __eq__(self, other):
        if type(other) is not SymbolGroup:
            return False
        return self.group == self.group

    def __hash__(self):
        return hash(self.group)
