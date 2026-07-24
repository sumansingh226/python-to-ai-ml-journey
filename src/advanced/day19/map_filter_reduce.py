"""
map(), filter(), reduce() in Python

What is map()?

map() applies a function to every item
in an iterable and returns a map object.

Syntax

map(function, iterable)

------------------------------------------------

What is filter()?

filter() selects only those elements
that satisfy a condition.

Syntax

filter(function, iterable)

------------------------------------------------

What is reduce()?

reduce() repeatedly applies a function
to reduce multiple values into a single value.

Syntax

from functools import reduce

reduce(function, iterable)

------------------------------------------------

Why do we use them?

1. Process collections efficiently.
2. Write cleaner code.
3. Avoid manual loops.
4. Used in Data Science.
5. Used in AI/ML preprocessing.
"""

from functools import reduce


# ==========================================
# Example 1 : map()
# ==========================================

numbers = [1, 2, 3, 4, 5]

squares = map(lambda x: x * x, numbers)

print(list(squares))

print()


# Example 2 : map() with Function
# ==========================================

def cube(number):
    return number ** 3

numbers = [1, 2, 3, 4]

result = map(cube, numbers)

print(list(result))

print()


# Example 3 : Convert to Uppercase
# ==========================================

names = ["python", "java", "c++"]

result = map(str.upper, names)

print(list(result))

print()


# ==========================================
# Example 4 : filter()
# ==========================================

numbers = [1,2,3,4,5,6,7,8,9,10]

even = filter(lambda x: x % 2 == 0, numbers)

print(list(even))

print()