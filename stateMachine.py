#!/bin/python3.4
# coding=utf-8
#MKA:xkondu00


class Redefinition(BaseException):
    pass


class Invalid(BaseException):
    pass


class MissingRule(BaseException):
    pass


class NotFinishing(BaseException):
    pass


class FiniteStateMachine(object):

    def __init__(self, rules_only=False, line_comment="#", post_comment=" "):
        self.states = dict()
        self.rules_only = rules_only
        self.alphabet = list()
        self.current = None
        self.buffer = str()
        self.last_handler = None
        self.output = dict()
        self.line_comment = line_comment
        self.post_comment = post_comment
        self.in_line_comment = False

    def add_state(self, name, starting=False, finishing=False):
        if (name in self.states):
            if (self.rules_only):
                return False
            raise Redefinition(name)
        self.states[name] = State(name, starting, finishing)
        return True

    def add_rule(self, starting, target, symbol, returning=False):
        if not self.rules_only:
            if (starting not in self.states or
                        target not in self.states or
                        symbol not in self.alphabet
                    ):
                raise Invalid("Missing state or symbol in definition")
        else:
            self.add_state(starting)
            self.add_state(target)
        symbol = self._symbol_decode(symbol)
        target = self.states[target]
        return self.states[starting].add_rule(symbol, target, returning)

    def add_symbol(self, symbol):
        if (self._symbol_collision(symbol)):
            raise Redefinition(symbol)
        if type(symbol) is tuple or type(symbol) is list:
            self.alphabet += symbol
        else:
            self.alphabet.append(symbol)

    def set_finishing(self, name):
        state = self.states[name]
        state.set_finishing()

    def _symbol_collision(self, symbol):
        if (type(symbol) is not tuple and type(symbol) is not list):
            if symbol in self.alphabet:
                return True
        return False

    def _symbol_decode(self, symbol):
        if len(symbol) > 1 and symbol[0] == "!":
            return SymbolGroup(symbol)
        return symbol

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
                self.add_rule(state, target, trans[0], ret)

    def set_starting(self, name):
        self.current = self.states[name]

    def step(self, char):
        if self.line_comment == char:
            if self.current.get_name() != "left_ap":
                self.in_line_comment = True
                return self.current
        if self.in_line_comment:
            if char == "\n":
                self.in_line_comment = False
                return self.step(self.post_comment)
            return self.current

        if not self.current:
            raise Invalid("Starting state not set")

        retval = self.current.step(char)
        if retval is None:
            raise MissingRule("Missing rule for: %s at state: %s"
                              % (char, self.current.get_name()))
        self.current = retval[0]
        self.handle_output(char, retval[1])
        return retval[0]

    def handle_output(self, char, handler):
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
            return True
        except MissingRule:
            return False

    def is_finishing(self):
        return self.current.is_finishing()


class State(object):

    def __init__(self, name, starting, finishing):
        self.name = name
        self.starting = starting
        self.finishing = finishing
        self.rules = dict()

    def add_rule(self, symbol, target, returning):
        if symbol in self.rules:
            raise Redefinition("%s in %s" % (symbol in self.name))
        self.rules[symbol] = (target, returning)

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
