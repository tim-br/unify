"""
Classic Prolog list operations
"""

from pyunify import Var, run, member, append, reverse, length

def main():
    print("="*70)
    print("LIST OPERATIONS")
    print("="*70)
    
    # member/2
    print("\n1. member(X, [1, 2, 3])")
    X = Var('X')
    for solution in run(member(X, [1, 2, 3]), X=X):
        print(f"  X = {solution.X}")
    
    # member/2 - checking membership
    print("\n2. member(2, [1, 2, 3])?")
    solutions = list(run(member(2, [1, 2, 3])))
    print(f"  {'Yes' if solutions else 'No'}")
    
    # append/3
    print("\n3. append([1, 2], [3, 4], Z)?")
    Z = Var('Z')
    for solution in run(append([1, 2], [3, 4], Z), Z=Z):
        print(f"  Z = {solution.Z}")
    
    # append/3 - reverse direction
    print("\n4. append([1, 2], Y, [1, 2, 3, 4])?")
    Y = Var('Y')
    for solution in run(append([1, 2], Y, [1, 2, 3, 4]), Y=Y):
        print(f"  Y = {solution.Y}")
    
    # append/3 - another direction
    print("\n5. append(X, [3, 4], [1, 2, 3, 4])?")
    X = Var('X')
    for solution in run(append(X, [3, 4], [1, 2, 3, 4]), X=X):
        print(f"  X = {solution.X}")
    
    # reverse/2
    print("\n6. reverse([1, 2, 3], R)?")
    R = Var('R')
    for solution in run(reverse([1, 2, 3], R), R=R):
        print(f"  R = {solution.R}")
    
    # length/2
    print("\n7. length([a, b, c], N)?")
    N = Var('N')
    for solution in run(length(['a', 'b', 'c'], N), N=N):
        print(f"  N = {solution.N}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
