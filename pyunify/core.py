"""
Core logic programming primitives using Python generators.

The key insight: generators ARE Prolog's search strategy.
- yield = success (like Prolog's clause succeeding)
- return/exhaustion = failure (triggers backtracking)
- generator composition = logical conjunction
"""

from typing import Any, Iterator, Optional, List, Dict, Callable
from dataclasses import dataclass
import copy
import threading

# Thread-local storage for controlling backtracking behavior
_local = threading.local()

# ============================================================================
# LOGIC VARIABLES - The heart of unification
# ============================================================================

class Var:
    """
    A logic variable that can be unified with values.
    
    Think of it as a placeholder that can be filled in exactly once
    (within a solution branch).
    """
    
    _counter = 0
    
    def __init__(self, name: Optional[str] = None):
        self.id = Var._counter
        Var._counter += 1
        self.name = name or f"_G{self.id}"
        self._binding = None  # Current binding in this search branch
    
    def __repr__(self):
        if self.is_bound():
            return f"{self.name}={self.deref()}"
        return f"?{self.name}"
    
    def is_bound(self) -> bool:
        """Is this variable currently bound?"""
        return self._binding is not None
    
    def deref(self) -> Any:
        """
        Dereference - follow chains of variables to get the actual value.
        
        Example: X -> Y -> 42, deref(X) returns 42
        """
        if not self.is_bound():
            return self
        
        val = self._binding
        # Follow chains
        if isinstance(val, Var):
            return val.deref()
        return val
    
    @property
    def value(self) -> Any:
        """Convenience property for dereferencing"""
        return self.deref()


# ============================================================================
# UNIFICATION - Pattern matching that can work in any direction
# ============================================================================

def unify(a: Any, b: Any) -> Iterator[None]:
    """
    Unify two terms, yielding once if successful.

    Unification is like pattern matching but works in ANY direction:
    - unify(X, 5) binds X to 5
    - unify([1, X], [Y, 2]) binds X to 2 and Y to 1
    - unify(X, Y) makes X and Y refer to the same unknown

    The magic: we save/restore bindings as we backtrack through
    the generator, giving us automatic undo for free!
    """
    # Check if we're in "no backtracking" mode
    no_backtrack = getattr(_local, 'no_backtrack', False)

    # Dereference to get actual values
    a_val = a.deref() if isinstance(a, Var) else a
    b_val = b.deref() if isinstance(b, Var) else b

    # Case 1: Both are the same value
    if a_val is b_val:
        yield
        return

    # Case 2: One or both are unbound variables
    if isinstance(a_val, Var):
        # Bind a to b, yield success, then unbind on backtrack (unless disabled)
        old_binding = a_val._binding
        a_val._binding = b_val
        yield
        if not no_backtrack:
            a_val._binding = old_binding  # Automatic undo!
        return

    if isinstance(b_val, Var):
        old_binding = b_val._binding
        b_val._binding = a_val
        yield
        if not no_backtrack:
            b_val._binding = old_binding
        return
    
    # Case 3: Both are equal non-variable values
    if a_val == b_val:
        yield
        return
    
    # Case 4: Both are lists - unify element by element
    if isinstance(a_val, list) and isinstance(b_val, list):
        if len(a_val) != len(b_val):
            return  # Different lengths = failure
        
        yield from unify_all(zip(a_val, b_val))
        return
    
    # Case 5: Both are tuples
    if isinstance(a_val, tuple) and isinstance(b_val, tuple):
        if len(a_val) != len(b_val):
            return
        yield from unify_all(zip(a_val, b_val))
        return
    
    # Case 6: Both are dicts (for pattern matching on objects)
    if isinstance(a_val, dict) and isinstance(b_val, dict):
        # Match all keys in a_val
        for key in a_val:
            if key not in b_val:
                return
        
        pairs = [(a_val[k], b_val[k]) for k in a_val]
        yield from unify_all(pairs)
        return
    
    # No other cases match = failure (no yield)


def unify_all(pairs: List[tuple]) -> Iterator[None]:
    """
    Unify all pairs in sequence (conjunction).
    
    This is the essence of logical AND with backtracking:
    - Try to unify first pair
    - If successful, recursively unify the rest
    - If any fails, backtrack
    """
    if not pairs:
        yield  # All unified successfully!
        return
    
    (a, b), *rest = pairs
    
    # Try to unify first pair
    for _ in unify(a, b):
        # Success! Try the rest
        yield from unify_all(rest)


# ============================================================================
# LOGICAL OPERATORS - Composing generators
# ============================================================================

def AND(*goals) -> Iterator[None]:
    """
    Logical AND - all goals must succeed.
    
    Each goal is a generator. We run them in sequence,
    backtracking if any fails.
    
    Example:
        yield from AND(
            unify(X, 1),
            unify(Y, 2),
            lambda: (yield) if X.value + Y.value == 3 else None
        )
    """
    if not goals:
        yield
        return
    
    first, *rest = goals
    
    # Handle both generators and generator functions
    gen = first() if callable(first) else first
    
    for _ in gen:
        yield from AND(*rest)


def OR(*goals) -> Iterator[None]:
    """
    Logical OR - try each goal, yielding all successes.
    
    Example:
        yield from OR(
            unify(X, 1),
            unify(X, 2),
            unify(X, 3)
        )
        # Tries X=1, then X=2, then X=3
    """
    for goal in goals:
        gen = goal() if callable(goal) else goal
        yield from gen


def ONCE(goal) -> Iterator[None]:
    """
    Succeed at most once (like Prolog's !).
    
    Takes first solution and stops.
    """
    gen = goal() if callable(goal) else goal
    for _ in gen:
        yield
        return


# ============================================================================
# QUERY EXECUTION - Capturing solutions
# ============================================================================

@dataclass
class Solution:
    """
    A solution is a snapshot of variable bindings.
    
    Provides attribute access: solution.X, solution.Y, etc.
    """
    vars: Dict[str, Var]
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_') or name == 'vars':
            return object.__getattribute__(self, name)
        
        if name in self.vars:
            var = self.vars[name]
            return var.value if var.is_bound() else var
        
        raise AttributeError(f"No variable named '{name}'")
    
    def __repr__(self):
        items = []
        for name, var in self.vars.items():
            if var.is_bound():
                items.append(f"{name}={var.value}")
            else:
                items.append(f"{name}=?")
        return f"Solution({', '.join(items)})"
    
    def get(self, name: str, default=None) -> Any:
        """Get a variable value, or default if not bound"""
        try:
            return getattr(self, name)
        except AttributeError:
            return default


def run(goal, **vars) -> Iterator[Solution]:
    """
    Execute a query and yield all solutions.

    Example:
        X = Var('X')
        Y = Var('Y')

        for solution in run(parent(X, Y), X=X, Y=Y):
            print(f"{solution.X} is parent of {solution.Y}")

    Alternative: pass vars as dict
        for solution in run(parent(X, Y), vars={'X': X, 'Y': Y}):
            ...
    """
    # Execute the goal
    gen = goal() if callable(goal) else goal

    for _ in gen:
        # Capture current variable bindings by creating new Vars with the dereferenced values
        snapshot = {}
        for name, var in vars.items():
            if isinstance(var, Var):
                # Create a new Var bound to the current dereferenced value
                new_var = Var(name)
                new_var._binding = var.deref()
                snapshot[name] = new_var
            else:
                snapshot[name] = var
        yield Solution(vars=snapshot)


def run_one(goal, **vars) -> Optional[Solution]:
    """Get the first solution only"""
    return next(run(goal, **vars), None)


def run_all(goal, **vars) -> List[Solution]:
    """Get all solutions as a list"""
    return list(run(goal, **vars))


def once(goal) -> bool:
    """
    Run goal once and commit the bindings (no backtracking).

    This allows a simpler API where you can access variable values
    directly after the call without needing to capture them in a Solution.

    Example:
        x = Var('X')
        y = Var('Y')

        if once(lambda: parent(x, y)):
            print(f"{x.value} is parent of {y.value}")

    Args:
        goal: A callable that returns a generator, or a generator itself

    Returns:
        True if the goal succeeded at least once, False otherwise
    """
    # Enable no-backtracking mode
    old_value = getattr(_local, 'no_backtrack', False)
    _local.no_backtrack = True

    try:
        # Call the goal to create the generator AFTER setting no_backtrack
        gen = goal() if callable(goal) else goal

        # Try to get first solution
        try:
            next(gen)
            # Success! Close the generator (bindings will stay because no_backtrack is True)
            gen.close()
            return True
        except StopIteration:
            return False
    finally:
        # Restore previous backtracking mode
        _local.no_backtrack = old_value


# ============================================================================
# HELPER PREDICATES - Common patterns
# ============================================================================

def succeed() -> Iterator[None]:
    """Always succeeds once (like Prolog's true)"""
    yield


def fail() -> Iterator[None]:
    """Always fails (like Prolog's fail)"""
    return
    yield  # Never reached


def eq(a, b) -> Iterator[None]:
    """Alias for unify"""
    yield from unify(a, b)


# ============================================================================
# TRACING - Debug your logic programs
# ============================================================================

_trace_enabled = False
_trace_depth = 0

def trace_on():
    """Enable tracing"""
    global _trace_enabled
    _trace_enabled = True

def trace_off():
    """Disable tracing"""
    global _trace_enabled
    _trace_enabled = False

def traced(name: str):
    """
    Decorator to trace predicate calls.
    
    Example:
        @traced("parent")
        def parent(x, y):
            # ... implementation
            yield
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            global _trace_depth
            
            if _trace_enabled:
                indent = "  " * _trace_depth
                args_str = ", ".join(str(a) for a in args)
                print(f"{indent}CALL: {name}({args_str})")
            
            _trace_depth += 1
            try:
                gen = func(*args, **kwargs)
                solution_count = 0
                
                for result in gen:
                    solution_count += 1
                    if _trace_enabled:
                        indent = "  " * (_trace_depth - 1)
                        print(f"{indent}SUCCESS: {name} (solution {solution_count})")
                    yield result
                
                if _trace_enabled and solution_count == 0:
                    indent = "  " * (_trace_depth - 1)
                    print(f"{indent}FAIL: {name}")
            
            finally:
                _trace_depth -= 1
        
        return wrapper
    return decorator


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'Var',
    'unify', 'unify_all',
    'AND', 'OR', 'ONCE',
    'run', 'run_one', 'run_all',
    'Solution',
    'succeed', 'fail', 'eq',
    'trace_on', 'trace_off', 'traced'
]
