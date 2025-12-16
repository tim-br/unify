"""
backtrack - Logic Programming for Python

Prolog's power with Python's clarity, using generators for backtracking.
"""

from .core import (
    Var,
    unify, unify_all, eq,
    AND, OR, ONCE,
    run, run_one, run_all, once,
    Solution,
    succeed, fail,
    trace_on, trace_off, traced
)

from .predicates import (
    member, append, length, reverse, last, nth,
    between, succ, plus, times,
    not_unifiable, different,
    findall
)

__version__ = '0.1.0'

__all__ = [
    # Core
    'Var', 'unify', 'unify_all', 'eq',
    'AND', 'OR', 'ONCE',
    'run', 'run_one', 'run_all', 'once', 'Solution',
    'succeed', 'fail',
    'trace_on', 'trace_off', 'traced',

    # Predicates
    'member', 'append', 'length', 'reverse', 'last', 'nth',
    'between', 'succ', 'plus', 'times',
    'not_unifiable', 'different',
    'findall',
]
