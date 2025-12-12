"""Test simple API"""

from pyunify import Var, member, unify, run, AND, OR

def test_unify(x):
    """Example predicate that unifies x with a member of [1, 2, 3]"""
    q = Var('Q')
    yield from AND(
        lambda: member(q, [1, 2, 3]),
        lambda: unify(q, x)
    )

def test_compose(x, y):
    """Compose two test_unify calls with AND - demonstrates predicate composition"""
    yield from AND(
        lambda: test_unify(x),
        lambda: test_unify(y)
    )

def test_compose_or(x, y):
    """Compose test_unify calls with OR - demonstrates OR behavior"""
    yield from OR(
        lambda: test_unify(x),
        lambda: test_unify(y)
    )

def main():
    print("="*70)
    print("SIMPLE API TEST")
    print("="*70)

    # Test 1: Using run() - all solutions
    print("\nTest 1: Using run() - all solutions")
    x = Var('X')
    for solution in run(test_unify(x), X=x):
        print(f"  x = {solution.X}")

    # Test 2: Just get first solution
    print("\nTest 2: Just first solution")
    y = Var('Y')
    solution = next(run(test_unify(y), Y=y), None)
    if solution:
        print(f"  y = {solution.Y}")

    # Test 3: Chaining unifications
    print("\nTest 3: Chaining unifications")
    x2 = Var('X')
    sol = next(run(test_unify(x2), X=x2), None)
    if sol:
        print(f"  x2 = {sol.X}")
        v = Var('V')
        sol2 = next(run(unify(sol.X, v), V=v), None)
        if sol2:
            print(f"  v = {sol2.V}")

    # Test 4: Composing predicates with AND - shows backtracking!
    print("\nTest 4: Composing predicates with AND (test_compose)")
    print("  (Should get 3x3 = 9 solutions from backtracking)")
    x3 = Var('X')
    y3 = Var('Y')
    for solution in run(test_compose(x3, y3), X=x3, Y=y3):
        print(f"  X = {solution.X}, Y = {solution.Y}")

    # Test 5: Composing predicates with OR - shows alternative solutions
    print("\nTest 5: Composing predicates with OR (test_compose_or)")
    print("  (OR tries first branch, then second branch)")
    x4 = Var('X')
    y4 = Var('Y')
    for solution in run(test_compose_or(x4, y4), X=x4, Y=y4):
        print(f"  X = {solution.X}, Y = {solution.Y}")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
