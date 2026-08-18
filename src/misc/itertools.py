""" 
The itertools module is a built-in Python library that provides a collection of fast, memory-efficient tools for working with iterators. Instead of loading entire lists into memory, itertools processes data one item at a time, making it incredibly powerful for large datasets or complex mathematical operations.

The functions in itertools generally fall into three main categories:

1. Combinatoric Iterators
These are used to generate mathematical combinations and permutations. They are excellent replacements for deeply nested for loops.

product(): Calculates the Cartesian product of input iterables (equivalent to nested loops).

permutations(): Generates all possible orderings of an iterable.

combinations(): Generates all possible combinations of a specific length, where order does not matter.
"""


import itertools

# product: Cartesian product (like a nested loop)
list(itertools.product(['A', 'B'], [1, 2])) 
# Output: [('A', 1), ('A', 2), ('B', 1), ('B', 2)]

# permutations: Order matters
list(itertools.permutations([1, 2, 3], 2))
# Output: [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# combinations: Order doesn't matter
list(itertools.combinations([1, 2, 3], 2))
# Output: [(1, 2), (1, 3), (2, 3)]