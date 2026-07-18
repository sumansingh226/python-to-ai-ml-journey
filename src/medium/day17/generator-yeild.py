"""
Generators in Python

What is a Generator?

A generator is a special type of function
that returns one value at a time instead
of returning all values at once.

Generators use the 'yield' keyword.

------------------------------------------------

Why do we use Generators?

1. Save memory.
2. Process large datasets.
3. Produce values lazily (on demand).
4. Improve performance.
5. Used heavily in AI/ML and Data Science.

------------------------------------------------

Difference

Function
---------
Returns all at once.

Generator
----------
Returns one value at a time.
"""


# Example 1 : Normal Function
# ==========================================

def numbers():

    return [1, 2, 3, 4, 5]


print(numbers())


print()


# ==========================================
# Example 2 : Generator Function
# ==========================================

def numbers():

    yield 1
    yield 2
    yield 3
    yield 4
    yield 5


generator = numbers()

print(generator)


print()


