Intro
=====

A Moore's finite state machine  implemented in python3.

This repository was created for a project to Principles of Programming Languages
class at Faculty of Information technology at Brno University of Technology.

``stateMachine.py`` contains general Moore's finite state machine implementation.

``mka.py`` contains specific use-case defined by the project.


stateMachine.py
---------------

class FiniteStateMachine
^^^^^^^^^^^^^^^^^^^^^^^^
Holds all information about finite state machine.

 .. code:: python

    stateMachine.FiniteStateMachine(
        rules_only=False,
        line_comment="#",
        allow_redefinition=True,
        escape_state="left_ap"
    )

``rules_only`` - If True when adding rules starting state or targeted state don't have to exist and are created. Exception is raised if set to False and states don't exist.

``line_comment`` - Ignore lines starting with this string.

``allow_redefinition`` - If False and you create state with same name or same transition as existing Exception is raised.

``escape_state`` - States which name ``contains`` this sub-string  are read literally. (Allows escape characters that are same as control characters when creating state machine from config file.)

method add_state(name, finishing=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add state to finite state machine.

``name`` - Name of the state.

``finishing`` - Set to as finishing state.

returns - True if added successfully.

raise Redefinition - If state already exists

method add_symbol(symbol)
~~~~~~~~~~~~~~~~~~~~~~~~~
Add symbol to the set of symbols. If `rules_only` is set then this method has no effect.

``symbol`` - String to add to state machine's alphabet.

returns - True if added successfully.

raise Redefinition - If symbol already exists

method add_rule(starting_name, target_name, symbol, returning=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add transition rule to state machine.

``starting_name`` - Name of the starting state.

``target_name`` - Name of the targeted state.

``symbol`` - String to make the transition.

``returning`` (string or False) - Symbol is saved to the cache. When more transition in row are made with the same ``returning`` string then those symbols are concatenated in the cache.

returns - True if added successfully.

raise Invalid if states or symbol in rule doesn't exists

raise Nondeterminism if rule with same starting state and symbol but different target exists

method set_finishing(name)
~~~~~~~~~~~~~~~~~~~~~~~~~~
Set State with "name" as finishing

``name`` - Name of the state to set as finishing.

raise Invalid  -If State with given name doesn't exists.

method set_starting(name)
~~~~~~~~~~~~~~~~~~~~~~~~~
Set starting state of state machine, the state is also always set as the current one.

``name`` - Name of the state to set as starting (current).

raise Invalid  -If State with given name doesn't exists.

method step(char)
~~~~~~~~~~~~~~~~~
Make transition from current state with symbol.
New current state is set accordingly.

``char`` - Symbol to make transition with.

returns - Instance of State class of targeted state, that is set as current.

raise MissingRule - If there is no rule for given symbol from current state.

method read_string(string)
~~~~~~~~~~~~~~~~~~~~~~~~~~
Read string symbol by symbol and make transitions starting from current state.

returns - True if last state is finishing, false otherwise.

raise MissingRule - If there is no rule for given symbol from current state.

method build_from_config(conf)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Add FSM's components from config file.

``conf`` - configparser.ConfigParser object

Config must have following structure:

 .. code:: ini

    [start]   # from state start
    start = a    # go to start with symbol "a"
    finish = b    # go to finish with symbol "b"
        handler     # optional handler for capturing sequences
    [finish.]   # from state finish
                # if ends with dot "." then it's finishing state
    finish = a,b # go to finish with "a" or "b"

This file must be read this way:

 .. code:: python

    conf = configparser.ConfigParser()
    conf.read(conf_path)
    machine = stateMachine.FiniteStateMachine()
    machine.build_from_config(conf)
    machine.set_starting('start')

method is_finishing()
~~~~~~~~~~~~~~~~~~~~~
returns - True if current state is finishing, False otherwise.

method is_WSFA()
~~~~~~~~~~~~~~~~~~~~~
returns - True if the state machine is `well specified finite automata`, False otherwise.

method minimize()
~~~~~~~~~~~~~~~~~
Minimize state machine.

returns - New instance of FiniteStateMachine that is minimized version of this state machine.

method find_non_terminating()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Finds not terminating state of the state machine.

returns:
    1) name of non-terminating state

    2) "0" if no non-terminating state exists

    3) False if more than one non-terminating state exists


class SymbolGroup()
^^^^^^^^^^^^^^^^^^^
When adding symbol using FiniteStateMachine.add_symbol(symbol)
you can set one of following to specify group of characters:

 - ``"!ALPHA"``
 - ``"!ALPHANUM"``
 - ``"!ALPHANUM_"``
 - ``"!SPACE"``
 - ``"!LF"``
 - ``"!SKIP"``
 - ``"!NOTAPOST"``
 - ``"!NOTAPOST_CHAR"``

class Redefinition(BaseException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Raised when rule, symbol or state should be created but already exist.

class Invalid(BaseException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Raised when state or symbol is not defined when creating rule.

class MissingRule(BaseException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Raised when transition should be made with `symbol` from `state` but there is no such a rule.

class Nondeterminism(BaseException)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Raised when rule from `state` with `symbol` to `target` should be created but already exist to `different target`.

Requires
========

-  python >= 3.4
