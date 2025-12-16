"""
Family tree - demonstrating logic programming in Python
"""

from unify import Var, unify, run, traced, OR, AND

# Define our facts as a Python data structure
PARENTS = [
    ('abraham', 'homer'),
    ('abraham', 'herb'),
    ('mona', 'homer'),
    ('homer', 'bart'),
    ('homer', 'lisa'),
    ('homer', 'maggie'),
    ('marge', 'bart'),
    ('marge', 'lisa'),
    ('marge', 'maggie'),
]

GENDERS = {
    'abraham': 'male',
    'homer': 'male',
    'herb': 'male',
    'bart': 'male',
    'mona': 'female',
    'marge': 'female',
    'lisa': 'female',
    'maggie': 'female',
}

# ============================================================================
# PREDICATES - Just generator functions!
# ============================================================================

def parent(x, y):
    """x is parent of y"""
    for p, c in PARENTS:
        # Try to unify with each fact
        for _ in unify(x, p):
            yield from unify(y, c)

def male(x):
    """x is male"""
    for person, gender in GENDERS.items():
        if gender == 'male':
            yield from unify(x, person)

def female(x):
    """x is female"""
    for person, gender in GENDERS.items():
        if gender == 'female':
            yield from unify(x, person)

# RULES - predicates calling predicates (with backtracking!)

def grandparent(x, z):
    """x is grandparent of z"""
    y = Var('Y')  # Intermediate variable
    yield from AND(
        lambda: parent(x, y),
        lambda: parent(y, z)
    )

def grandfather(x, z):
    """x is grandfather of z"""
    yield from AND(
        lambda: grandparent(x, z),
        lambda: male(x)
    )

def grandmother(x, z):
    """x is grandmother of z"""
    yield from AND(
        lambda: grandparent(x, z),
        lambda: female(x)
    )

def sibling(x, y):
    """x and y are siblings"""
    p = Var('P')
    yield from AND(
        lambda: parent(p, x),
        lambda: parent(p, y)
    )
    # Note: should add x != y constraint

def ancestor(x, y):
    """x is ancestor of y (recursive!)"""
    # Base case: parent is ancestor
    def base_case():
        yield from parent(x, y)

    # Recursive case: parent of ancestor
    def recursive_case():
        z = Var('Z')
        yield from AND(
            lambda: parent(x, z),
            lambda: ancestor(z, y)
        )

    # Try base case OR recursive case
    yield from OR(base_case, recursive_case)

# ============================================================================
# EXAMPLES
# ============================================================================

def main():
    print("="*70)
    print("FAMILY TREE - Logic Programming in Python")
    print("="*70)
    
    # Query 1: Who are Bart's parents?
    print("\n1. Who are Bart's parents?")
    X = Var('X')
    for solution in run(parent(X, 'bart'), X=X):
        print(f"  → {solution.X}")
    
    # Query 2: Who are Homer's children?
    print("\n2. Who are Homer's children?")
    X = Var('X')
    for solution in run(parent('homer', X), X=X):
        print(f"  → {solution.X}")
    
    # Query 3: Who are Bart's grandparents?
    print("\n3. Who are Bart's grandparents?")
    X = Var('X')
    for solution in run(grandparent(X, 'bart'), X=X):
        print(f"  → {solution.X}")
    
    # Query 4: Who are Abraham's grandchildren?
    print("\n4. Who are Abraham's grandchildren?")
    X = Var('X')
    for solution in run(grandparent('abraham', X), X=X):
        print(f"  → {solution.X}")
    
    # Query 5: All grandparent-grandchild pairs
    print("\n5. All grandparent-grandchild pairs:")
    X, Y = Var('X'), Var('Y')
    for solution in run(grandparent(X, Y), X=X, Y=Y):
        print(f"  → {solution.X} is grandparent of {solution.Y}")
    
    # Query 6: Who is Bart's grandfather?
    print("\n6. Who is Bart's grandfather?")
    X = Var('X')
    for solution in run(grandfather(X, 'bart'), X=X):
        print(f"  → {solution.X}")
    
    # Query 7: Bart's siblings
    print("\n7. Who are Bart's siblings?")
    X = Var('X')
    seen = set()
    for solution in run(sibling('bart', X), X=X):
        if solution.X != 'bart' and solution.X not in seen:
            seen.add(solution.X)
            print(f"  → {solution.X}")
    
    # Query 8: All of Bart's ancestors
    print("\n8. All of Bart's ancestors:")
    X = Var('X')
    seen = set()
    for solution in run(ancestor(X, 'bart'), X=X):
        if solution.X not in seen:
            seen.add(solution.X)
            print(f"  → {solution.X}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
