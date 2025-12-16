"""
Simple scheduling problem using unify

Problem: Schedule 3 tasks (A, B, C) into 3 time slots (1, 2, 3)
Constraints:
- Each task gets exactly one time slot
- Task B must come after Task A (dependency)
- Task C cannot be in slot 2 (resource constraint)
"""

from unify import Var, run, member, AND, unify, different

def less_than(x, y):
    """x < y (both must be bound)"""
    x_val = x.deref() if hasattr(x, 'deref') else x
    y_val = y.deref() if hasattr(y, 'deref') else y

    # Both must be bound to compare
    if not isinstance(x_val, Var) and not isinstance(y_val, Var):
        if x_val < y_val:
            yield

def not_in(var, value):
    """Variable must not equal value"""
    # Try all values except the forbidden one
    # This is a simple implementation - in practice we'd filter the domain
    v = var.deref() if hasattr(var, 'deref') else var
    if isinstance(v, Var):
        # Can't check yet if unbound - would need constraint propagation
        # For now, just succeed and let member/unify handle it
        yield
    elif v != value:
        yield

def main():
    print("="*70)
    print("TASK SCHEDULING PROBLEM")
    print("="*70)
    print("\nProblem:")
    print("  Schedule tasks A, B, C into time slots 1, 2, 3")
    print("\nConstraints:")
    print("  1. Each task gets a different time slot")
    print("  2. Task B must come after Task A")
    print("  3. Task C cannot be in slot 2")
    print("\nSearching for valid schedules...")
    print("-"*70)

    # Get all solutions
    task_a = Var('A')
    task_b = Var('B')
    task_c = Var('C')

    def schedule_with_vars():
        yield from AND(
            # Each task assigned to a slot 1, 2, or 3
            lambda: member(task_a, [1, 2, 3]),
            lambda: member(task_b, [1, 2, 3]),
            lambda: member(task_c, [1, 2, 3]),

            # Constraint: Task B must come after Task A (A < B)
            lambda: less_than(task_a, task_b),

            # Constraint: Task C cannot be in slot 2
            lambda: not_in(task_c, 2),

            # All tasks in different slots
            lambda: different(task_a, task_b),
            lambda: different(task_b, task_c),
            lambda: different(task_a, task_c),
        )

    solutions = list(run(schedule_with_vars(), A=task_a, B=task_b, C=task_c))

    if solutions:
        print(f"\nFound {len(solutions)} valid schedule(s):\n")
        for i, sol in enumerate(solutions, 1):
            print(f"Solution {i}:")
            print(f"  Task A → Slot {sol.A}")
            print(f"  Task B → Slot {sol.B}")
            print(f"  Task C → Slot {sol.C}")
            print(f"  Schedule: A@{sol.A}, B@{sol.B}, C@{sol.C}")
            print()
    else:
        print("\nNo valid schedules found!")

    print("="*70)

if __name__ == '__main__':
    main()
