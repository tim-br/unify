"""
Standard predicates - the Prolog standard library in Python
"""

from typing import Any, Iterator, List
from .core import Var, unify, unify_all, OR, AND

# ============================================================================
# LIST OPERATIONS
# ============================================================================

def member(item: Any, lst: Any) -> Iterator[None]:
    """
    item is a member of list.
    
    Works in multiple modes:
    - member(X, [1,2,3]) -> X = 1; X = 2; X = 3
    - member(2, [1,2,3]) -> true
    - member(X, Y) -> error (can't enumerate infinite lists)
    
    Classic Prolog:
        member(X, [X|_]).
        member(X, [_|Tail]) :- member(X, Tail).
    """
    # Get the actual list value
    lst_val = lst.value if isinstance(lst, Var) else lst
    
    if not isinstance(lst_val, list):
        return  # Not a list, fail
    
    # Try each element
    for elem in lst_val:
        yield from unify(item, elem)


def append(xs: Any, ys: Any, result: Any) -> Iterator[None]:
    """
    result is the concatenation of xs and ys.
    
    Multi-directional:
    - append([1,2], [3,4], Z) -> Z = [1,2,3,4]
    - append([1,2], Y, [1,2,3,4]) -> Y = [3,4]
    - append(X, [3,4], [1,2,3,4]) -> X = [1,2]
    
    Classic Prolog:
        append([], Ys, Ys).
        append([X|Xs], Ys, [X|Zs]) :- append(Xs, Ys, Zs).
    """
    # Base case: append([], Ys, Ys)
    for _ in unify(xs, []):
        yield from unify(ys, result)
    
    # Recursive case: append([X|Xs], Ys, [X|Zs])
    xs_val = xs.value if isinstance(xs, Var) else xs
    
    if isinstance(xs_val, list) and xs_val:
        head = xs_val[0]
        tail = xs_val[1:]
        
        # result must be [head|zs]
        z_tail = Var()
        
        for _ in unify(result, [head] + [z_tail]):
            # Recursively append tail
            yield from append(tail, ys, z_tail)


def length(lst: Any, n: Any) -> Iterator[None]:
    """
    n is the length of list.
    
    length([1,2,3], N) -> N = 3
    length(L, 3) -> generates lists of length 3
    """
    lst_val = lst.value if isinstance(lst, Var) else lst
    
    if isinstance(lst_val, list):
        # List is known, compute length
        yield from unify(n, len(lst_val))
    elif isinstance(n, int) or (isinstance(n, Var) and n.is_bound()):
        # Length is known, generate list
        n_val = n.value if isinstance(n, Var) else n
        vars = [Var(f"_E{i}") for i in range(n_val)]
        yield from unify(lst, vars)


def reverse(lst: Any, result: Any) -> Iterator[None]:
    """
    result is the reverse of lst.
    
    reverse([1,2,3], R) -> R = [3,2,1]
    """
    lst_val = lst.value if isinstance(lst, Var) else lst
    
    if isinstance(lst_val, list):
        yield from unify(result, list(reversed(lst_val)))


def last(lst: Any, item: Any) -> Iterator[None]:
    """item is the last element of lst"""
    lst_val = lst.value if isinstance(lst, Var) else lst
    
    if isinstance(lst_val, list) and lst_val:
        yield from unify(item, lst_val[-1])


def nth(n: Any, lst: Any, item: Any) -> Iterator[None]:
    """
    item is the nth element of lst (0-indexed).
    
    nth(1, [a,b,c], X) -> X = b
    """
    n_val = n.value if isinstance(n, Var) else n
    lst_val = lst.value if isinstance(lst, Var) else lst
    
    if isinstance(n_val, int) and isinstance(lst_val, list):
        if 0 <= n_val < len(lst_val):
            yield from unify(item, lst_val[n_val])


# ============================================================================
# ARITHMETIC & COMPARISON
# ============================================================================

def between(low: int, high: int, x: Any) -> Iterator[None]:
    """
    Generate integers from low to high (inclusive).
    
    between(1, 5, X) -> X = 1; X = 2; X = 3; X = 4; X = 5
    """
    for i in range(low, high + 1):
        yield from unify(x, i)


def succ(x: Any, y: Any) -> Iterator[None]:
    """
    y is the successor of x (y = x + 1).
    
    Works in both directions:
    - succ(5, Y) -> Y = 6
    - succ(X, 6) -> X = 5
    """
    x_val = x.value if isinstance(x, Var) else x
    y_val = y.value if isinstance(y, Var) else y
    
    if isinstance(x_val, (int, float)) and not isinstance(x_val, bool):
        yield from unify(y, x_val + 1)
    elif isinstance(y_val, (int, float)) and not isinstance(y_val, bool):
        yield from unify(x, y_val - 1)


def plus(x: Any, y: Any, z: Any) -> Iterator[None]:
    """
    z = x + y (works in any direction where 2 of 3 are known).
    
    plus(2, 3, Z) -> Z = 5
    plus(2, Y, 5) -> Y = 3
    plus(X, 3, 5) -> X = 2
    """
    x_val = x.value if isinstance(x, Var) else x
    y_val = y.value if isinstance(y, Var) else y
    z_val = z.value if isinstance(z, Var) else z
    
    x_known = not isinstance(x_val, Var)
    y_known = not isinstance(y_val, Var)
    z_known = not isinstance(z_val, Var)
    
    if x_known and y_known:
        yield from unify(z, x_val + y_val)
    elif x_known and z_known:
        yield from unify(y, z_val - x_val)
    elif y_known and z_known:
        yield from unify(x, z_val - y_val)


def times(x: Any, y: Any, z: Any) -> Iterator[None]:
    """z = x * y"""
    x_val = x.value if isinstance(x, Var) else x
    y_val = y.value if isinstance(y, Var) else y
    z_val = z.value if isinstance(z, Var) else z
    
    x_known = not isinstance(x_val, Var)
    y_known = not isinstance(y_val, Var)
    z_known = not isinstance(z_val, Var)
    
    if x_known and y_known:
        yield from unify(z, x_val * y_val)
    elif x_known and z_known and x_val != 0:
        yield from unify(y, z_val / x_val)
    elif y_known and z_known and y_val != 0:
        yield from unify(x, z_val / y_val)


# ============================================================================
# CONTROL FLOW
# ============================================================================

def not_unifiable(a: Any, b: Any) -> Iterator[None]:
    """
    Succeed if a and b do NOT unify.
    
    \+ (negation by failure in Prolog)
    """
    for _ in unify(a, b):
        return  # They unified, so we fail
    
    # They didn't unify, so we succeed
    yield


def different(a: Any, b: Any) -> Iterator[None]:
    """a and b are different (not unifiable)"""
    yield from not_unifiable(a, b)


# ============================================================================
# HIGHER-ORDER
# ============================================================================

def findall(template: Any, goal, result: Any) -> Iterator[None]:
    """
    Collect all solutions of goal into a list.
    
    findall(X, parent(X, 'bart'), Parents) -> Parents = [homer, marge]
    """
    solutions = []
    
    for _ in goal:
        # Capture the current value of template
        val = template.value if isinstance(template, Var) else template
        solutions.append(val)
    
    yield from unify(result, solutions)


__all__ = [
    'member', 'append', 'length', 'reverse', 'last', 'nth',
    'between', 'succ', 'plus', 'times',
    'not_unifiable', 'different',
    'findall'
]
