#!/bin/python3.4
# coding=utf-8
#MKA:xkondu00

from copy import copy
from itertools import combinations


class Redefinition(BaseException):
    pass


class Invalid(BaseException):
    pass


class MissingRule(BaseException):
    pass


class NotFinishing(BaseException):
    pass


class Nondeterminism(BaseException):
    pass


class FiniteStateMachine(object):

    def __init__(
        self,
        rules_only=False,
        line_comment="#",
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
        self.in_line_comment = False
        # for WSFA check
        self.reversed_rules = dict()
        self.dump_rules = dict()
        self.finishing = list()

    def __repr__(self):
        """
        Returns all FSM components in a formated string
        """
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
        """
        Add new state
        Raise Redefinition if state with a same name already exists
        Crate new State object
        """
        if (name in self.states):
            if self.rules_only or self.can_redef:
                return False
            raise Redefinition("Multiple states with name: %s" % name, "\n")

        self.states[name] = State(name, finishing)
        if finishing:
            self.finishing.append(name)
        return True

    def add_rule(self, starting_name, target_name, symbol, returning=False):
        """
        Add new rule
        Raise Invalid if states or symbol in rule doesn't exists
        Raise Nondeterminism if rule with same starting state and symbol
            but different target exists
        Add new rule to starting State object
        Add new record to self.dump_rules and self.reversed_rules for
            faster analysis
        """
        if not self.rules_only:
            if (
                starting_name not in self.states or
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
        elif not self.can_redef:
            raise Redefinition("%s in %s" % (symbol, self.name), "\n")
        return retval

    def add_symbol(self, symbol):
        """
        Add new symbol to alphabet
        Raise Redefinition if symbol already exists
        """
        if (self._symbol_collision(symbol)) and not self.rules_only:
            if self.can_redef:
                return False
            raise Redefinition("Symbol %s already declared" % symbol, "\n")
        if type(symbol) is tuple or type(symbol) is list:
            self.alphabet += symbol
        elif symbol not in self.alphabet:
            self.alphabet.append(symbol)
        else:
            return False
        return True

    def set_finishing(self, name):
        """
        Set State with "name" as finishing
        Raise Invalid if State with given name doesn't exists
        """
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
        """
        Set State with "name" as starting
        Raise Invalid if State with given name doesn't exists
        """
        if name in self.states:
            self.current = self.states[name]
        else:
            raise Invalid("Starting state doesn't exists", "\n")

    def build_from_config(self, conf):
        """
        Add FSM's components from config file.
        Config must have following structure:

        [start]   # from state start
        start = a    # go to start with symbol "a"
        finish = b    # go to finish with symbol "b"
            handler     # optional handler for capturing sequences
        [finish.]   # from state finish
                    # if ends with dot "." then it's finishing state
        finish = a,b # go to finish with "a" or "b"

        """
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
        """
        Returns new FiniteStateMachine object that is MFA for this one
        """
        # divide all states on finishing and non-finishing
        non_finishing = list()
        for state_name in self.states:
            if state_name not in self.finishing:
                non_finishing.append(state_name)
        states = [copy(self.finishing), non_finishing]
        states = [group for group in states if group]

        # divide group, if possible
        while True:
            # find group, to divide
            to_divide = self._find_group_to_divide(states)
            if to_divide:
                states.remove(to_divide)
                new_groups = self._divide_group(to_divide, states)
                states = states + list(new_groups)
            else:
                break
        # create new finite automata object
        new_fsm = FiniteStateMachine()
        starting_name = self.current.get_name()
        # merge states in same group and add them to new automat
        for group in states:
            group.sort()
            state_name = "_".join(group)
            finishing = False
            if group[0] in self.finishing:
                finishing = True
            new_fsm.add_state(state_name, finishing=finishing)
            if starting_name in group:
                new_fsm.set_starting(state_name)
        # add all symbols
        for symbol in self.alphabet:
            new_fsm.add_symbol(symbol)
        # add all rules
        for group in states:
            group.sort()
            state_name = "_".join(group)
            for symbol, target in self.states[group[0]]:
                for target_group in states:
                    if target in target_group:
                        target_group.sort()
                        target_name = "_".join(target_group)
                new_fsm.add_rule(state_name, target_name, symbol)
        # return new minimized FSM
        return new_fsm

    def _find_group_to_divide(self, states):
        for group in states:
            rules = dict()
            for state_name in group:
                state = self.states[state_name]
                for symbol in self.alphabet:
                    next_state = state.step(symbol)[0].get_name()
                    for target_group in states:
                        if next_state in target_group:
                            target = target_group
                            break
                    if symbol in rules:
                        if rules[symbol] != target:
                            return group
                    else:
                        rules[symbol] = target
        return None

    def _rules_for_group(self, group, states):
        rules = dict()
        for state_name in group:
            state = self.states[state_name]
            for symbol in self.alphabet:
                next_state = state.step(symbol)[0].get_name()
                for target_group in states:
                    if next_state in target_group:
                        target = target_group
                        break
                if symbol not in rules:
                    rules[symbol] = list()
                if target not in rules[symbol]:
                    rules[symbol].append(target)
        return rules

    def _divide_group(self, group, states):
        for count in range(1, -(-len(group) // 2) + 1):
            # all combinations of states in group
            # "-(-len(group) // 2) + 1" equals to roundUP(group_count/2)
            for tmp_two in combinations(group, count):
                group_two = list(tmp_two)
                tmp_states = copy(states)
                group_one = copy(group)
                for state in group_two:
                    group_one.remove(state)
                tmp_states.append(group_one)
                tmp_states.append(group_two)
                rules_one = self._rules_for_group(group_one, tmp_states)
                rules_two = self._rules_for_group(group_two, tmp_states)
                if not self._rules_interfere(rules_one, rules_two):
                    return group_one, group_two

    def _rules_interfere(self, one, two):
        for symbol in self.alphabet:
            set_one = set()
            set_two = set()
            for target in one[symbol]:
                set_one.add("_".join(target))
            for target in two[symbol]:
                set_two.add("_".join(target))
            if not set_one.intersection(set_two):
                return False
        return True

    def step(self, char):
        """
        Take one step from current state with char
        Set new current state and returns it
        If char is start of a line comment, then current state
            is returned. All symbols until LF are ignored.
        """
        if self.line_comment == char:
            if self.literally not in self.current.get_name():
                self.in_line_comment = True
                return self.current
        if self.in_line_comment:
            if char == "\n":
                self.in_line_comment = False
                return self.step(char)
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
        for char in string:
            if char == "'":
                char = "''"
            self.step(char)
        return self.is_finishing()

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
        """
        Checks if all states in FSA are accessible
        """
        accessible = [self.current.get_name(), ]
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

    def __iter__(self):
        """
        Iterates over all rules of this state
        Returns tuple: (symbol, target_name)
        """
        for symbol in self.rules:
            yield symbol, self.rules[symbol][0].get_name()

    def add_rule(self, symbol, target, returning):
        if symbol in self.rules:
            if target is self.rules[symbol][0]:
                return False
            else:
                raise Nondeterminism(
                    "Multiple targets for one symbol... nondeterminism", "\n")
        self.rules[symbol] = (target, returning)
        return True

    def finishing(self):
        return self.finishing

    def step(self, char):
        """
        Take one step with char
        Returns tuple: (new_state, handler)
        """
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
    """
    group characters with similar attribute
    """

    def __init__(self, group):
        self.group = group

    def __call__(self, char):
        """
        Returns True if char belongs to a group
            False otherwise
        """
        return {
            "!ALPHA": char.isalpha(),
            "!ALPHANUM": char.isalnum(),
            "!ALPHANUM_": char.isalnum() or char == "_",
            "!SPACE": char.isspace(),
            "!LF": char in "\n\r",
            "!SKIP": char not in "\n\r",
            "!NOTAPOST": char != "'",
            "!NOTAPOST_CHAR": char not in "'{}()->,.#" and not char.isspace()
        }[self.group]

    def __eq__(self, other):
        # necessary for beeing a key in dictionary and handling duplicity
        if type(other) is not SymbolGroup:
            return False
        return self.group == self.group

    def __hash__(self):
        # necessary for beeing a key in dictionary
        return hash(self.group)
