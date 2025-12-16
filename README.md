# unify

Logic programming in Python using generators for automatic backtracking.

## Overview

unify brings Prolog-style logic programming to Python with a clean, Pythonic API. It uses Python's generator mechanism to implement automatic backtracking, allowing you to write declarative logic programs that explore solution spaces naturally.

**Key Features:**
- **Automatic backtracking** via Python generators
- **Unification** that works in any direction
- **Logical operators** (AND, OR) that compose naturally
- **Built-in predicates** for lists, arithmetic, and more
- **Zero dependencies** - pure Python
- **Seamless integration** with imperative Python code

## Installation

**From GitHub:**

```bash
# Using uv (pinned to v0.1.0)
uv pip install git+https://github.com/tim-br/unify.git@v0.1.0

# Or using pip
pip install git+https://github.com/tim-br/unify.git@v0.1.0

# Or install latest main branch
uv pip install git+https://github.com/tim-br/unify.git
```

**In another project's `pyproject.toml`:**

```toml
[project]
dependencies = [
    # Pinned to v0.1.0 (recommended)
    "pyunify-logic @ git+https://github.com/tim-br/unify.git@v0.1.0",

    # Or use latest main branch
    # "pyunify-logic @ git+https://github.com/tim-br/unify.git",
]
```

**For development:**

```bash
# Clone the repository
git clone https://github.com/tim-br/unify.git
cd unify

# Install in editable mode
uv pip install -e .
```

## Quick Start

**Interactive Python session:**

```python
>>> from unify import Var, run, unify
>>>
>>> x = Var('X')
>>> for sol in run(unify(x, 42), X=x):
...     print(sol)
...
Solution(X=42)
```

**Complete example:**

```python
from unify import Var, run, member, AND

# Define a predicate
def test_unify(x):
    """Unify x with members of [1, 2, 3]"""
    q = Var('Q')
    yield from AND(
        lambda: member(q, [1, 2, 3]),
        lambda: unify(q, x)
    )

# Query for all solutions
x = Var('X')
for solution in run(test_unify(x), X=x):
    print(f"X = {solution.X}")

# Output:
# X = 1
# X = 2
# X = 3
```

## Core Concepts

### Logic Variables

Variables that can be unified with values or other variables:

```python
x = Var('X')
y = Var('Y')

# Unify X with 42
for _ in unify(x, 42):
    print(x.value)  # 42

# Unify two variables
for _ in unify(x, y):
    print(x.value is y.value)  # True (they reference each other)
```

### Predicates

Predicates are generator functions that yield once per solution:

```python
def parent(x, y):
    """x is parent of y"""
    for p, c in PARENTS:
        for _ in unify(x, p):
            yield from unify(y, c)

# Find all parent-child relationships
parent_var = Var('Parent')
child_var = Var('Child')
for sol in run(parent(parent_var, child_var), Parent=parent_var, Child=child_var):
    print(f"{sol.Parent} is parent of {sol.Child}")
```

### Logical Operators

**AND** - All goals must succeed:

```python
def grandparent(x, z):
    """x is grandparent of z"""
    y = Var('Y')
    yield from AND(
        lambda: parent(x, y),
        lambda: parent(y, z)
    )
```

**OR** - Try each alternative:

```python
def ancestor(x, y):
    """x is ancestor of y"""
    def base_case():
        yield from parent(x, y)

    def recursive_case():
        z = Var('Z')
        yield from AND(
            lambda: parent(x, z),
            lambda: ancestor(z, y)
        )

    yield from OR(base_case, recursive_case)
```

### Backtracking

The system automatically explores all solution paths:

```python
def test_compose(x, y):
    """Demonstrates backtracking with AND"""
    yield from AND(
        lambda: member(x, [1, 2, 3]),
        lambda: member(y, [1, 2, 3])
    )

x = Var('X')
y = Var('Y')
for sol in run(test_compose(x, y), X=x, Y=y):
    print(f"X={sol.X}, Y={sol.Y}")

# Output: All 9 combinations
# X=1, Y=1
# X=1, Y=2
# X=1, Y=3
# ... etc
```

## API Reference

### Core Functions

- **`Var(name=None)`** - Create a logic variable
- **`unify(a, b)`** - Unify two terms
- **`AND(*goals)`** - Logical conjunction
- **`OR(*goals)`** - Logical disjunction
- **`run(goal, **vars)`** - Execute query and yield all solutions
- **`run_one(goal, **vars)`** - Get first solution only
- **`run_all(goal, **vars)`** - Get all solutions as a list

### Built-in Predicates

**List Operations:**
- **`member(item, list)`** - item is a member of list
- **`append(xs, ys, result)`** - result is concatenation of xs and ys
- **`length(list, n)`** - list has length n

**Arithmetic:**
- **`plus(x, y, z)`** - z = x + y (works in any direction)
- **`minus(x, y, z)`** - z = x - y
- **`times(x, y, z)`** - z = x * y
- **`between(low, high, x)`** - x is between low and high (inclusive)

**Comparison:**
- **`gt(x, y)`** - x > y
- **`lt(x, y)`** - x < y
- **`gte(x, y)`** - x >= y
- **`lte(x, y)`** - x <= y

### Variable Methods

- **`var.is_bound()`** - Check if variable is bound
- **`var.deref()`** - Dereference to get actual value
- **`var.value`** - Property for dereferencing

## Examples

The `examples/` directory contains complete demonstrations:

### Family Tree (`family_tree.py`)
Demonstrates facts, rules, and recursive predicates:
```bash
uv run examples/family_tree.py
```

Shows how to:
- Define facts (parent, gender)
- Create rules (grandparent, sibling, ancestor)
- Use recursion for transitive relationships

### List Operations (`list_operations.py`)
Shows built-in list predicates:
```bash
uv run examples/list_operations.py
```

Demonstrates:
- `member/2` for list membership
- `append/3` for concatenation
- `length/2` for list length

### Simple API (`test_simple_api.py`)
Basic usage patterns and composition:
```bash
uv run examples/test_simple_api.py
```

Covers:
- Creating and querying predicates
- Composing with AND/OR
- Understanding backtracking behavior

## How It Works

unify uses Python generators to implement Prolog's search strategy:

- **`yield`** = success (one solution found)
- **`return`** = failure (triggers backtracking)
- **Generator composition** = logical conjunction
- **Automatic unbinding** on backtrack via `try/finally` in generators

When you call `next()` on a generator, it continues from where it left off, naturally implementing backtracking.

## Design Philosophy

unify embraces **hybrid programming**:
- Use logic programming for queries, search, and constraint satisfaction
- Use imperative Python for I/O, computation, and side effects
- Seamlessly integrate both paradigms in the same program

This gives you the power of declarative logic programming without giving up Python's ecosystem.

## License

MIT
